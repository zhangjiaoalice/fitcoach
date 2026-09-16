/// <reference types="vite/client" />

declare module "*.vue" {
  import type { DefineComponent } from "vue";
  // 官方推荐写法：三个 any 让 props/emits 由组件自身推导
  const component: DefineComponent<{}, {}, any>;
  export default component;
}
