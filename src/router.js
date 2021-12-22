import Vue from 'vue'
import Router from 'vue-router'
import IGV from "./components/IGV";


Vue.use(Router);

const routes = [
    { path: "/", component: IGV },
    { path: "/home", redirect: "/" },
    { path: '/*',  component: () => import('./components/404.vue') }
];


const originalPush = Router.prototype.push
   Router.prototype.push = function push(location) {
   return originalPush.call(this, location).catch(err => err)
}


const router = new Router({
    routes: routes,
});


window.router = router;

export default router