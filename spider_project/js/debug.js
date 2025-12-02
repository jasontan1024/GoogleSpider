/**
 * 页面调试信息提取器
 * 用于获取页面基本信息以便调试
 */
function getPageInfo() {
    return {
        title: document.title,
        url: window.location.href,
        bodyText: document.body.innerText.substring(0, 500),
        hasDivG: document.querySelectorAll('div.g').length,
        hasH3: document.querySelectorAll('h3').length,
        allLinks: Array.from(document.querySelectorAll('a[href]')).slice(0, 10).map(a => a.href)
    };
}

