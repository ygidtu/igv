#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
from typing import List, Optional
import click
from flask import Flask, send_file, render_template, jsonify, request
from utils import *
# from flask_cors import CORS


__dir__ = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(__dir__, "dist/"),
    static_url_path="/static",
    template_folder=os.path.join(__dir__, "dist/")
)
# CORS(app)

app.config["path"] = os.path.join(__dir__, "config.json")
app.config["data"] = load_config(app.config["path"])


@app.route("/")
async def root():
    return render_template("index.html")


@app.route("/files")
async def files():
    
    data = app.config["data"]
    key = request.args.get('key')
    file = request.args.get('file')
    index = request.args.get('index', False)
    
    if file:
        f = data.get("BAM", {})
        f = f.get(key, {})
        f = f.get(file, "")
        
        if index:
            f = f + (".bai" if f.endswith(".bam") else ".tbi")
        
        return send_file(f, as_attachment = True, attachment_filename=os.path.basename(f))
    
    def decode(b):
        bak = b
        try:  
            b = b.split("_")
            b[0] = re.sub(r"[^\d_]", "", b[0])
            
            if len(b) > 1:
                n = int(re.sub(r"[^\d]", "", b[1]))
                scale = 1 if re.search(r"\d+D", b[1]) else 30
                b[1] = n * scale

            b = [int(x) for x in b]
            if len(b) < 2:
                b.append(100000)
        except Exception:
            b = [int(hash(bak)), 100000]
        return b
    
    res = {}
    for i, j in data["BAM"].items():
        res[i] = sorted(j.keys(), key=decode)

    return jsonify(res)


@app.get("/ref")
async def reference():
    data = app.config["data"]

    filetype = request.args.get('filetype')
    index = request.args.get('index', False)
    print(filetype, index)
    if filetype == "fasta":
        f = data.get("FASTA") if not index else data.get("FASTA", "") + ".fai"
    else:
        f = data.get("REFERENCE") if not index else data.get("REFERENCE", "") + ".tbi"
    return send_file(f, as_attachment = True, attachment_filename=os.path.basename(f))


@click.command()
@click.option(
    "-h", "--host",
    type=str,
    default = "127.0.0.1",
    help=""" The host address. """, 
    show_default=True
)
@click.option(
    "-p", "--port",
    type=int,
    default=5000,
    help=""" The port listen to. """, 
    show_default=True
)
@click.option(
    "-k", "--key",
    type=click.Path(exists=True),
    help=""" The path to ssl key file. """
)
@click.option(
    "-c", "--cert",
    type=click.Path(exists=True),
    help=""" The path to ssl cert file. """, 
    show_default=True
)
@click.option(
    "-g", "--gtf",
    type=click.Path(exists=True),
    required=True,
    help=""" The path to reference gtf file. """, 
    show_default=True
)
@click.option(
    "-f", "--fasta",
    type=click.Path(exists=True),
    required=True,
    help=""" The path to fasta file. """, 
    show_default=True
)
@click.option(
    "-b", "--bam",
    type=click.Path(exists=True),
    required=True,
    help=""" The path to directory contains bam files. """, 
    show_default=True
)
@click.version_option("0.0.1", message="Current version %(version)s")
def main(
    host: str, port: int,
    fasta: str, bam: str, gtf: str,
    key: str, cert: str
):
    if not os.path.exists(gtf + ".tbi"):
        gtf = index_gtf(gtf)
    
    if not os.path.exists(fasta + ".fai"):
        index_fasta(fasta)
        
    save_config({
        "BAM": collect_bam(bam),
        "REFERENCE": gtf,
        "FASTA": fasta
    },  app.config["path"])
    
    if key and cert:
        app.run(
            host=host,
            port=port,
            ssl_context=(cert, key),
            threaded = True
        )
    else:
        app.run(
            host=host,
            port=port,
            threaded = True,
            debug = True
        )
    
if __name__ == '__main__':
    main()

    