import { createApp } from "vue";

import App from "./App.vue";
import router from "./router";
import {getToken, clearToken} from './api/client';
import {me} from './api/auth';
import "./styles/theme.css";

const app = createApp(App);

async function bootstrap() {
    const token = getToken();
    if (token) {
        try{
            // 启动前检查
            await me();
        } catch(err: any) {
            // 401 清除 token
            if (err.status === 401) {
                clearToken();
            }
        }
    }
    app.use(router).mount("#app");
}

bootstrap();
