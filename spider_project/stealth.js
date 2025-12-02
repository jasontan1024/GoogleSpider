/**
 * 反检测脚本 - 在页面加载前注入
 * 用于隐藏 webdriver 特征，避免被检测为自动化浏览器
 */

// 隐藏 webdriver 特征
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});

// 修改 Chrome 对象
window.chrome = {
    runtime: {}
};

// 修改权限查询
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
);

// 修改插件数组
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});

// 修改语言数组
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en']
});

// 覆盖 toString 方法
window.navigator.webdriver = undefined;

