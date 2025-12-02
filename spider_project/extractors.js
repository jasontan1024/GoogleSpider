/**
 * 谷歌搜索结果提取器
 * 从配置中读取选择器并提取搜索结果
 */
function extractSearchResults(config) {
    const results = [];
    
    // 尝试多种可能的选择器来找到结果容器
    // 注意：div.g 不是唯一的，一页搜索结果通常有10个div.g容器
    // 每个 div.g 代表一个搜索结果，包含标题、链接、描述
    // 使用 querySelectorAll 查找所有匹配的容器
    const containerSelectors = config.selectors.result_container.primary;
    let elements = [];
    
    for (const selector of containerSelectors) {
        elements = Array.from(document.querySelectorAll(selector));  // 查找所有匹配的容器（不是唯一的）
        if (elements.length > 0) {
            console.log(`找到 ${elements.length} 个搜索结果容器，使用选择器: ${selector}`);
            break;
        }
    }
    
    // 提取每个结果
    // 注意：所有选择器都在当前结果容器（el）范围内查找，不会匹配到页面其他地方的相同标签
    elements.forEach((el, index) => {
        try {
            // 提取标题 - 在容器范围内查找
            // 使用 el.querySelector() 确保只在当前结果容器内查找，不会匹配到页面其他地方的 h3
            let titleEl = null;
            const titleSelectors = config.selectors.title.selectors;
            for (const selector of titleSelectors) {
                titleEl = el.querySelector(selector);  // 在容器 el 内查找
                if (titleEl) break;
            }
            
            // 提取链接 - 在容器范围内查找
            // 优先从标题元素向上查找包含它的a标签（最准确，适用于95%+的情况）
            // 如果失败，则查找符合特定模式的链接（避免匹配到导航链接等）
            let linkEl = null;
            const urlSelectors = config.selectors.url.selectors;
            for (const selector of urlSelectors) {
                if (selector.includes('closest')) {
                    // 从标题向上查找父级a标签（情况1：标题在链接内，最准确）
                    // closest() 会向上查找，但标题在容器内，所以找到的链接也一定在容器内
                    if (titleEl) {
                        linkEl = titleEl.closest('a');
                        // 验证找到的链接是否在容器内（防止意外匹配到容器外的链接）
                        if (linkEl && linkEl.getAttribute('href') && el.contains(linkEl)) {
                            break;
                        } else {
                            linkEl = null;
                        }
                    }
                } else {
                    // 在容器范围内查找符合特定模式的链接，避免匹配到导航链接等非搜索结果
                    // 使用 el.querySelectorAll() 确保只在当前结果容器内查找
                    const links = el.querySelectorAll(selector);
                    for (const link of links) {
                        const href = link.getAttribute('href');
                        if (!href) continue;
                        
                        const linkText = link.textContent.trim().toLowerCase();
                        
                        // 过滤掉明显不是搜索结果的链接
                        const isInvalid = 
                            href === '#' ||  // 空链接
                            href.startsWith('javascript:') ||  // JS链接
                            (href.includes('#') && !href.startsWith('http') && !href.startsWith('/url?q=')) ||  // 锚点链接（但保留Google重定向链接）
                            linkText.includes('更多') ||  // "更多结果"
                            linkText.includes('more') ||  // "More"
                            linkText.includes('相关') ||  // "相关搜索"
                            linkText.includes('related') ||  // "Related"
                            linkText.includes('next') ||  // "Next"
                            linkText.includes('上一页') ||  // "上一页"
                            linkText.includes('previous');  // "Previous"
                        
                        if (!isInvalid) {
                            linkEl = link;
                            break;
                        }
                    }
                    if (linkEl) break;
                }
            }
            
            // 提取描述 - 在容器范围内查找
            // 使用 el.querySelector() 确保只在当前结果容器内查找，不会匹配到页面其他地方的描述
            let descEl = null;
            const descSelectors = config.selectors.description.selectors;
            for (const selector of descSelectors) {
                descEl = el.querySelector(selector);  // 在容器 el 内查找
                if (descEl) break;
            }
            
            if (titleEl && linkEl) {
                let url = linkEl.getAttribute('href');
                
                // 处理谷歌的 URL 重定向
                if (url && url.startsWith(config.extraction.url_redirect_prefix)) {
                    try {
                        const urlParams = new URLSearchParams(url.split('?')[1]);
                        url = urlParams.get('q') || url;
                    } catch (e) {
                        // 如果解析失败，保持原URL
                    }
                }
                
                // 确保是完整URL
                if (url && !url.startsWith('http')) {
                    url = config.extraction.base_url + url;
                }
                
                results.push({
                    title: titleEl.textContent.trim(),
                    url: url,
                    description: descEl ? descEl.textContent.trim() : ''
                });
            }
        } catch (e) {
            console.error(`提取第 ${index} 个结果时出错:`, e);
        }
    });
    
    return results;
}

/**
 * 执行提取并返回结果
 * 这个函数会被Python代码调用
 */
function executeExtraction(config) {
    return extractSearchResults(config);
}

