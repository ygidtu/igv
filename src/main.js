import Vue from 'vue';

import axios from 'axios';
import VueAxios from 'vue-axios';

import {
  Backtop,
  Col,
  Container,
  Header,
  Icon,
  Main,
  Row,
  Transfer
} from 'element-ui';

import router from './router'

import App from './App.vue';
import 'element-ui/lib/theme-chalk/index.css';


Vue.use(Backtop);
Vue.use(Col);
Vue.use(Container);
Vue.use(Header);
Vue.use(Icon);
Vue.use(Main);
Vue.use(Row);
Vue.use(Transfer);

Vue.config.productionTip = false;
Vue.prototype.log = console.log;
Vue.use(VueAxios, axios);

new Vue({
  router,
  render: h => h(App),
}).$mount('#app');
