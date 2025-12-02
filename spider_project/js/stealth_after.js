/**
 * 增强版反检测脚本 - 在页面加载后执行
 * 用于删除 automation 相关属性和进一步伪装
 */

// ========== 删除 Chrome DevTools Protocol 痕迹 ==========
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;

// 删除所有可能的自动化标识
Object.keys(window).forEach(key => {
    if (key.includes('cdc_') || key.includes('__playwright') || key.includes('__pw_')) {
        try {
            delete window[key];
        } catch (e) {}
    }
});

// ========== 覆盖 webdriver ==========
Object.defineProperty(navigator, 'webdriver', {
    get: () => false,
    configurable: true
});

// ========== 修改 iframe 检测 ==========
const originalContentWindow = Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'contentWindow').get;
Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
    get: function() {
        const window = originalContentWindow.call(this);
        try {
            Object.defineProperty(window, 'navigator', {
                value: new Proxy(navigator, {
                    has: () => true,
                    get: (target, prop) => {
                        if (prop === 'webdriver') return false;
                        return target[prop];
                    }
                })
            });
        } catch (e) {}
        return window;
    }
});

// ========== 覆盖 Notification 权限 ==========
const originalNotification = window.Notification;
window.Notification = function(title, options) {
    return new originalNotification(title, options);
};
Object.setPrototypeOf(window.Notification, originalNotification);
Object.defineProperty(window.Notification, 'permission', {
    get: () => 'default'
});

// ========== 修改 Battery API ==========
if (navigator.getBattery) {
    const originalGetBattery = navigator.getBattery;
    navigator.getBattery = function() {
        return originalGetBattery.call(this).then(battery => {
            Object.defineProperty(battery, 'charging', {
                get: () => true,
                configurable: true
            });
            Object.defineProperty(battery, 'chargingTime', {
                get: () => 0,
                configurable: true
            });
            Object.defineProperty(battery, 'dischargingTime', {
                get: () => Infinity,
                configurable: true
            });
            Object.defineProperty(battery, 'level', {
                get: () => 1,
                configurable: true
            });
            return battery;
        });
    };
}

// ========== 修改媒体设备 ==========
if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
    const originalEnumerateDevices = navigator.mediaDevices.enumerateDevices;
    navigator.mediaDevices.enumerateDevices = function() {
        return originalEnumerateDevices.call(this).then(devices => {
            return devices.map(device => {
                const newDevice = {...device};
                if (device.deviceId === 'default' || device.deviceId.length < 10) {
                    newDevice.deviceId = 'default';
                }
                return newDevice;
            });
        });
    };
}

// ========== 覆盖 toString 方法 ==========
const originalToString = Function.prototype.toString;
Function.prototype.toString = function() {
    if (this === navigator.webdriver) {
        return 'function webdriver() { [native code] }';
    }
    return originalToString.apply(this, arguments);
};

// ========== 添加真实的用户交互痕迹 ==========
// 模拟页面交互
setTimeout(() => {
    // 随机滚动
    if (Math.random() > 0.5) {
        window.scrollTo({
            top: Math.random() * document.body.scrollHeight,
            left: 0,
            behavior: 'smooth'
        });
    }
    
    // 模拟鼠标移动
    const event = new MouseEvent('mousemove', {
        view: window,
        bubbles: true,
        cancelable: true,
        clientX: Math.random() * window.innerWidth,
        clientY: Math.random() * window.innerHeight
    });
    document.dispatchEvent(event);
}, 2000 + Math.random() * 3000);
