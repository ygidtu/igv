#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Created by ygidtu at 2018.12.19

Inspired by SplicePlot -> mRNAObjects
"""
import os
import re
import gzip
import filetype
import json
from glob import glob

import pysam


class GenomicLoci(object):
    u"""
    Created by ygidtu at 2018.12.19

    A base class to handle the position relationships
    """

    __slots__ = [
        "chromosome",
        "start",
        "end",
        "strand",
        "gtf_line"
    ]

    def __init__(self, chromosome, start, end, strand, gtf_line=None):
        u"""
        init this class
        :param chromosome: str
        :param start: int
        :param end: int
        :param strand: str
        """

        self.chromosome = chromosome

        self.start = int(start)
        self.end = int(end)
        self.gtf_line = gtf_line

        if self.end < self.start:
            raise ValueError("End site should bigger than start site, not %d -> %d" % (self.start, self.end))
        if strand == ".":
            strand = "*"
        if strand not in ("+", "-", "*"):
            raise ValueError("strand should be + or -, not %s" % strand)

        self.strand = strand

    def __str__(self):
        u"""
        convert this to string
        :return:
        """
        return "{chromosome}:{start}-{end}:{strand}".format(
            **{
                "chromosome": self.chromosome,
                "start": self.start,
                "end": self.end,
                "strand": self.strand
            }
        )

    def __gt__(self, other):
        u"""
        whether this loci is downstream of other

        Note:
            make sure the wider range is upstream of narrower

            due to the sort of gtf file, therefore the transcript will be ahead of exons
        :param other:
        :return:
        """
        if self.chromosome != other.chromosome:
            return self.chromosome > other.chromosome

        if self.start != other.start:
            return self.start > other.start

        return self.end < other.end

    def __lt__(self, other):
        u"""
        whether this loci is upstream of other

        Note:
            make sure the wider range is downstream of narrower

            due to the sort of gtf file, therefore the transcript will be ahead of exons
        :param other:
        :return:
        """
        if self.chromosome != other.chromosome:
            return self.chromosome < other.chromosome

        if self.start != other.start:
            return self.start < other.start

        return self.end > other.end

    def __eq__(self, other):
        u"""
        whether two loci is the same
        :param other:
        :return:
        """
        return self.chromosome == other.chromosome and \
            self.start == other.start and \
            self.end == other.end

    def __add__(self, other):
        u"""
        merge two sites into one
        :param other:
        :return:
        """
        return GenomicLoci(
            chromosome=self.chromosome,
            start=min(self.start, other.start),
            end=max(self.end, other.end),
            strand=self.strand
        )

    def __hash__(self):
        u"""
        generate hash
        :return:
        """
        return hash((self.chromosome, self.start, self.end))

    @property
    def length(self):
        u"""
        :return: int, the length of this loci
        """
        return self.end - self.start

    def is_overlap(self, other):
        u"""
        whether two loci have any overlaps
        :param other: another GenomicLoci and it's children class
        :return: Boolean
        """
        return self.chromosome == other.chromosome and \
            self.start <= other.end and \
            self.end >= other.start

    @classmethod
    def create_loci(cls, string):
        u"""
        Create loci from String
        :param string: chr1:1-100:+
        :return:
        """
        temp = string.split(":")

        if len(temp) == 3:
            chromosome, sites, strand = temp
        elif len(temp) == 2:
            chromosome, sites = temp
            strand = "*"
        else:
            raise ValueError("Failed to decode genomic region: %s" % string)

        start, end = sites.split("-")

        return cls(chromosome, start, end, strand)


def is_gtf(infile):
    u"""
    check if input file is gtf
    :param infile: path to input file
    :return:
    """
    if infile is None:
        return False

    is_gtf = 0
    try:
        if filetype.guess_mime(infile) == "application/gzip":
            is_gtf += 10
            r = gzip.open(infile, "rt")
        else:
            r = open(infile)
    except TypeError as err:
        print("failed to open %s", infile)
        exit(err)

    for line in r:
        if line.startswith("#"):
            continue

        lines = re.split(r"\s+", line)

        if len(lines) < 8:
            break

        if re.search(
            r"([\w-]+ \"[\w.\s\-%,:]+\";? ?)+",
            " ".join(lines[8:])
        ):
            is_gtf += 1

        break

    r.close()

    return is_gtf


def is_bam(infile):
    u"""
    check if input file is bam or sam file
    :param infile: path to input file
    :return: Boolean
    """

    try:
        create = False
        if not os.path.exists(infile + ".bai"):
            create = True
        elif os.path.getctime(infile + ".bai") < os.path.getctime(infile):
            try:
                os.remove(infile + ".bai")
                create = True
            except PermissionError as err:
                print(err)
                create = False
        else:
            try:
                with pysam.AlignmentFile(infile) as r:
                    r.check_index()
            except ValueError:
                create = True

        if create:
            print("Creating index for %s" % infile)
            pysam.index(infile)
        return True

    except pysam.utils.SamtoolsError:
        return False


def index_gtf(input_gtf, sort_gtf=True, retry=0):
    """
    Created by ygidtu

    Extract only exon tags and keep it clean

    :param input_gtf: path to input gtf file
    :param sort_gtf: Boolean value, whether to sort gtf file first
    :param retry: only try to sort gtf once
    :return path to compressed and indexed bgzipped gtf file
    """
    if input_gtf is None:
        return None
    gtf = is_gtf(input_gtf)

    if gtf % 10 != 1:
        raise ValueError(f"gtf file required, {input_gtf} seems not a valid gtf file")

    index = False
    if gtf // 10 > 0:
        output_gtf = input_gtf
    else:
        output_gtf = input_gtf + ".gz"
    if not os.path.exists(output_gtf) or not os.path.exists(output_gtf + ".tbi"):
        index = True

    elif os.path.getctime(output_gtf) < os.path.getctime(
        output_gtf
    ) or os.path.getctime(output_gtf) < os.path.getctime(output_gtf):
        index = True

    # 2018.12.21 used to handle gtf not sorted error
    if sort_gtf and retry > 1:
        raise OSError(
            "Create index for %s failed, and trying to sort it failed too" % input_gtf
        )
    elif sort_gtf:
        data = []

        print("Sorting %s" % input_gtf)

        old_input_gtf = input_gtf
        input_gtf = re.sub(r"\.gtf$", "", input_gtf) + ".sorted.gtf"

        output_gtf = input_gtf + ".gz"

        if os.path.exists(input_gtf) and os.path.exists(output_gtf):
            return output_gtf

        try:
            w = open(input_gtf, "w+")
        except IOError as err:
            print("could not sort gtf")
            exit(1)

        with open(old_input_gtf) as r:
            for line in r:
                if line.startswith("#"):
                    w.write(line)
                    continue

                lines = line.split()

                if len(lines) < 1:
                    continue

                data.append(
                    GenomicLoci(
                        chromosome=lines[0],
                        start=lines[3],
                        end=lines[4],
                        strand=lines[6],
                        gtf_line=line,
                    )
                )

        for i in sorted(data, key=lambda x: [x.chromosome, x.start]):
            w.write(i.gtf_line)

        w.close()

    if index:
        print("Create index for %s", input_gtf)
        try:
            pysam.tabix_index(input_gtf, preset="gff", force=True, keep_original=True)
        except OSError as err:

            if re.search("could not open", str(err)):
                raise err

            print(err)
            print("Guess gtf needs to be sorted")
            return index_gtf(input_gtf=input_gtf, sort_gtf=True, retry=retry + 1)

    return output_gtf


def index_fasta(input_fasta):
    pysam.faidx(input_fasta)


def index_bam(input_bam):
    if not os.path.exists(input_bam + ".bai"):
        pysam.index(input_bam)
    return input_bam


def index_bedgraph(input_bdg):
    if not os.path.exists(input_bdg + ".tbi"):
        pysam.tabix_index(
            input_bdg, 
            seq_col=1, 
            start_col=2, 
            end_col=3, 
            force=True, 
            keep_original=True
        )
    return input_bdg
    

def collect_bam(inpath):
    fs = [os.path.join(inpath, i) for i in os.listdir(inpath)]
    fs = [f for f in fs if re.search(r"\.(bam|bdg|bedgraph)(\.gz)?$", f, re.I)]
    if fs:
        temp = {}
        for x in fs:
            temp[os.path.basename(x)] = index_bam(x) if x.endswith(".bam") else index_bedgraph(x)
        return {"Files": temp}
    else:
        dirs = [os.path.join(inpath, x) for x in os.listdir(inpath)]
        
        res = {}
        for x in dirs:
            if os.path.isdir(x):
                fs = [os.path.join(x, i) for i in os.listdir(x)]
                temp = {}
                for f in fs:
                    if re.search(r"\.(bam|bdg|bedgraph)(\.gz)?$", f, re.I):
                        temp[os.path.basename(f)] = index_bam(f) if f.endswith(".bam") else index_bedgraph(f)
                if temp:                        
                    res[os.path.basename(x)] = temp

        return res
        
        
def save_config(data, path: str):
    with open(path, "w+") as w:
        json.dump(data, w, indent = "    ")
        

def load_config(path: str):
    if os.path.exists(path):
        with open(path,  "r") as r:
            return json.load(r)
    return {}


if __name__ == '__main__':
    pass
