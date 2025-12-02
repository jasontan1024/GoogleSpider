/**
 * 反检测脚本 - 在页面加载后执行
 * 用于删除 automation 相关属性
 */

// 删除 automation 相关属性
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;

// 覆盖 webdriver
Object.defineProperty(navigator, 'webdriver', {
    get: () => false
});

