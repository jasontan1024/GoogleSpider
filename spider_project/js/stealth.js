/**
 * 增强版反检测脚本 - 在页面加载前注入
 * 用于隐藏 webdriver 特征，模拟真实浏览器环境
 */

// ========== 核心反检测 ==========

// 1. 隐藏 webdriver 特征（多种方式）
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});

// 删除 webdriver 属性
delete navigator.__proto__.webdriver;

// 覆盖 webdriver toString
const originalToString = Function.prototype.toString;
Function.prototype.toString = function() {
    if (this === navigator.webdriver) {
        return 'function webdriver() { [native code] }';
    }
    return originalToString.apply(this, arguments);
};

// 2. 修改 Chrome 对象（更完整）
if (!window.chrome) {
    window.chrome = {};
}
window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {}
};

// 3. 修改权限查询
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
);

// 4. 修改插件数组（更真实）
Object.defineProperty(navigator, 'plugins', {
    get: () => {
        const plugins = [
            {
                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                description: "Portable Document Format",
                filename: "internal-pdf-viewer",
                length: 1,
                name: "Chrome PDF Plugin"
            },
            {
                0: {type: "application/pdf", suffixes: "pdf", description: ""},
                description: "",
                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                length: 1,
                name: "Chrome PDF Viewer"
            },
            {
                0: {type: "application/x-nacl", suffixes: "", description: "Native Client Executable"},
                1: {type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable"},
                description: "",
                filename: "internal-nacl-plugin",
                length: 2,
                name: "Native Client"
            }
        ];
        plugins.item = function(index) { return this[index] || null; };
        plugins.namedItem = function(name) { return this[name] || null; };
        return plugins;
    }
});

// 5. 修改语言数组
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en', 'zh-CN', 'zh']
});

// 6. 修改硬件并发数（模拟真实设备）
Object.defineProperty(navigator, 'hardwareConcurrency', {
    get: () => 8
});

// 7. 修改设备内存
Object.defineProperty(navigator, 'deviceMemory', {
    get: () => 8
});

// 8. 修改平台信息
Object.defineProperty(navigator, 'platform', {
    get: () => 'Win32'
});

// 9. 修改连接信息
Object.defineProperty(navigator, 'connection', {
    get: () => ({
        effectiveType: '4g',
        rtt: 50,
        downlink: 10,
        saveData: false,
        onchange: null
    })
});

// 10. 覆盖 toString 和 valueOf
window.navigator.webdriver = undefined;
Object.defineProperty(navigator, 'webdriver', {
    configurable: true,
    get: () => false
});

// ========== Canvas 指纹保护 ==========
const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
HTMLCanvasElement.prototype.toDataURL = function(type) {
    if (type === 'image/png') {
        const context = this.getContext('2d');
        if (context) {
            const imageData = context.getImageData(0, 0, this.width, this.height);
            for (let i = 0; i < imageData.data.length; i += 4) {
                imageData.data[i] += Math.floor(Math.random() * 3) - 1;
            }
            context.putImageData(imageData, 0, 0);
        }
    }
    return originalToDataURL.apply(this, arguments);
};

// ========== WebGL 指纹保护 ==========
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) {
        return 'Intel Inc.';
    }
    if (parameter === 37446) {
        return 'Intel Iris OpenGL Engine';
    }
    return getParameter.apply(this, arguments);
};

// ========== 音频指纹保护 ==========
const AudioContext = window.AudioContext || window.webkitAudioContext;
if (AudioContext) {
    const originalCreateAnalyser = AudioContext.prototype.createAnalyser;
    AudioContext.prototype.createAnalyser = function() {
        const analyser = originalCreateAnalyser.apply(this, arguments);
        const originalGetFloatFrequencyData = analyser.getFloatFrequencyData;
        analyser.getFloatFrequencyData = function(array) {
            originalGetFloatFrequencyData.apply(this, arguments);
            for (let i = 0; i < array.length; i++) {
                array[i] += Math.random() * 0.0001;
            }
        };
        return analyser;
    };
}

// ========== 时间戳保护 ==========
const originalDate = Date;
Date = function(...args) {
    if (args.length === 0) {
        return new originalDate();
    }
    return new originalDate(...args);
};
Date.now = originalDate.now;
Date.parse = originalDate.parse;
Date.UTC = originalDate.UTC;
Date.prototype = originalDate.prototype;

// ========== 鼠标和键盘事件 ==========
// 添加真实的鼠标移动事件监听器
document.addEventListener('DOMContentLoaded', function() {
    // 模拟鼠标移动
    let mouseX = Math.random() * window.innerWidth;
    let mouseY = Math.random() * window.innerHeight;
    
    setInterval(() => {
        mouseX += (Math.random() - 0.5) * 10;
        mouseY += (Math.random() - 0.5) * 10;
        mouseX = Math.max(0, Math.min(window.innerWidth, mouseX));
        mouseY = Math.max(0, Math.min(window.innerHeight, mouseY));
        
        const event = new MouseEvent('mousemove', {
            view: window,
            bubbles: true,
            cancelable: true,
            clientX: mouseX,
            clientY: mouseY
        });
        document.dispatchEvent(event);
    }, 1000 + Math.random() * 2000);
});
