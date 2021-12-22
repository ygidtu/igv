<template>
  <div class="hello">
    <el-row justify="center">
      <el-col :span="8">
        <el-row v-for="key in keys" :key="key" >
          <el-col >
            <el-transfer 
            filterable 
            v-model="value" 
            :data="bam[key]" 
            :titles="[key, '已选中']" 
            @change="initIGV"
            />
          </el-col>
        </el-row>
      </el-col>

      <el-col :span="16" id="igv_anchor">
        <div id="igv" style="width: 100%; height: 1200px"></div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import igv from "igv";

export default {
  name: "IGV",
  props: {
    msg: String,
  },
  data() {
    return {
      keys: [],
      bam: {},
      bams: [],
      value: [],
      locus: "chr1:1271280-1272080"
    };
  },
  methods: {
    createURL(...urls) {
      let res = [];

      // let temp = document.getElementById("Prefix").value.replace(/(^\/|\/$)/g, "");
      // let temp = "http://192.168.194.241:8002";
      // if (temp !== "") {
      //   res.push(temp);
      // }

      for (let i = 0; i < urls.length; i++) {
        let temp = urls[i].toString();
        temp = temp.replace(/(^\/|\/$)/g, "");

        if (temp !== "") {
          res.push(temp);
        }
      }

      return res.join("/");
    },
    getParams() {
      const self = this;
      this.axios.get(self.createURL("/files")).then(response => {
        let idx = 0
        for (const [key, value] of Object.entries(response.data)) {
          // it's quite strange the v-for do not render bam in object format?
          let temp = [];
          for (let i in value) {
            temp.push({
              key: idx,
              label: value[i],
              group: key
            })
            idx = idx + 1
            self.bams.push({
              key: idx,
              label: value[i],
              group: key
            })
          }
          self.keys.push(key);
          self.bam[key] = temp;
        }
      })
    },
    initIGV() {
      // just replace the old browser with new one
      if (document.getElementById("igv_anchor")) {
          let p = document.getElementById("igv_anchor")
          var newElement = document.createElement("div");
          newElement.setAttribute('id', "igv");
          newElement.setAttribute("style", "width:100%; height: 1200px");
          p.replaceChild(newElement, p.childNodes[0])
      }

      let tracks = [];
      for (let v of this.value) {
        let b = this.bams[v]

        if (b.label.endsWith(".bam")) {
          tracks.push({
            type: "alignment",
            format: "bam",
            displayMode: "squished",
            name: `${b.group} - ${b.label}`,
            url: this.createURL(`/files?file=${b.label}&key=${b.group}`),
            indexURL: this.createURL(`/files?file=${b.label}&index=true&key=${b.group}`),
          });
        } else {
          tracks.push({
            type: "wig",
            format: "bedgraph",
            displayMode: "squished",
            name: `${b.group} - ${b.label}`,
            url: this.createURL(`/files?file=${b.label}&key=${b.group}`),
            indexURL: this.createURL(`/files?file=${b.label}&index=true&key=${b.group}`),
          });
        }
      }
      console.log(tracks)
      let igvDiv = document.getElementById("igv");

      if (this.value.length > 0) {
        igv.createBrowser(igvDiv, {
          genome: {
            id: "Genome",
            name: "Genome",
            fastaURL: this.createURL("ref?filetype=fasta"),
            indexURL: this.createURL("ref?filetype=fasta&index=true"),
            tracks: [
              {
                name: "Reference",
                type: "annotation",
                format: "gtf",
                displayMode: "expanded",
                height: 300,
                url: this.createURL("ref?filetype=gtf"),
                indexURL: this.createURL("ref?filetype=gtf&index=true"),
                visibilityWindow: 1000000,
                colorBy: "biotype",
                colorTable: {
                  antisense: "blueviolet",
                  protein_coding: "blue",
                  retained_intron: "rgb(0, 150, 150)",
                  processed_transcript: "purple",
                  processed_pseudogene: "#7fff00",
                  unprocessed_pseudogene: "#d2691e",
                  "*": "black",
                },
              },
            ],
          },
          locus: this.locus,
          tracks: tracks,
        });
      }

    },
  },
  mounted() {
      this.getParams();
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
