<template>
  <div id="app">
    <el-container>
      <el-main id="main" :style="{height: windowHeight + 'px'}">
        <IGV msg="Welcome to Your Vue.js App"/>
        <el-backtop target="#main" :visibility-height="50"/>
      </el-main>
  </el-container>
  </div>
</template>

<script>
import IGV from './components/IGV.vue'

export default {
  name: 'App',
  components: {
    IGV
  },
  computed: {
    windowHeight: function() {
      var igv = document.getElementById("igv")

      if (igv) {
        return window.innerHeight + igv.scrollHeight
      }
      return window.innerHeight
    }
  },
}
</script>

<style>
html { overflow-y: auto }

body { overflow: hidden; }

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  overflow-y: hidden
}

.el-main {
  background-color: #E9EEF3;
  color: #333;
}

.el-transfer-panel{
  width: 300px;
}

.el-scrollbar {
  overflow-y: hidden
}
</style>
