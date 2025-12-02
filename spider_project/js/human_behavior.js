/**
 * 人类行为模拟脚本
 * 模拟真实的鼠标移动、滚动、点击等行为
 */

(function() {
    'use strict';
    
    // ========== 鼠标移动模拟 ==========
    function simulateMouseMove() {
        let lastX = Math.random() * window.innerWidth;
        let lastY = Math.random() * window.innerHeight;
        
        const moveMouse = () => {
            const targetX = lastX + (Math.random() - 0.5) * 200;
            const targetY = lastY + (Math.random() - 0.5) * 200;
            
            const steps = 10 + Math.floor(Math.random() * 10);
            let currentStep = 0;
            
            const animate = () => {
                if (currentStep >= steps) {
                    lastX = targetX;
                    lastY = targetY;
                    setTimeout(moveMouse, 1000 + Math.random() * 3000);
                    return;
                }
                
                const progress = currentStep / steps;
                const easeProgress = progress * (2 - progress); // ease-out
                
                const x = lastX + (targetX - lastX) * easeProgress;
                const y = lastY + (targetY - lastY) * easeProgress;
                
                const event = new MouseEvent('mousemove', {
                    view: window,
                    bubbles: true,
                    cancelable: true,
                    clientX: x,
                    clientY: y,
                    movementX: x - lastX,
                    movementY: y - lastY
                });
                
                document.dispatchEvent(event);
                currentStep++;
                requestAnimationFrame(animate);
            };
            
            animate();
        };
        
        setTimeout(moveMouse, 1000 + Math.random() * 2000);
    }
    
    // ========== 滚动模拟 ==========
    function simulateScrolling() {
        setTimeout(() => {
            const scrollAmount = 100 + Math.random() * 400;
            const scrollDuration = 500 + Math.random() * 1000;
            const startTime = Date.now();
            const startScroll = window.pageYOffset;
            const targetScroll = Math.min(
                startScroll + scrollAmount,
                document.body.scrollHeight - window.innerHeight
            );
            
            const scroll = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / scrollDuration, 1);
                const easeProgress = progress * (2 - progress); // ease-out
                
                window.scrollTo(0, startScroll + (targetScroll - startScroll) * easeProgress);
                
                if (progress < 1) {
                    requestAnimationFrame(scroll);
                } else {
                    // 继续滚动或回滚
                    setTimeout(() => {
                        if (Math.random() > 0.5) {
                            simulateScrolling();
                        } else {
                            // 回滚一部分
                            window.scrollTo({
                                top: window.pageYOffset - (50 + Math.random() * 100),
                                behavior: 'smooth'
                            });
                        }
                    }, 2000 + Math.random() * 3000);
                }
            };
            
            scroll();
        }, 3000 + Math.random() * 5000);
    }
    
    // ========== 键盘事件模拟 ==========
    function simulateKeyboardEvents() {
        // 偶尔模拟键盘输入（Tab键等）
        setTimeout(() => {
            if (Math.random() > 0.7) {
                const tabEvent = new KeyboardEvent('keydown', {
                    key: 'Tab',
                    code: 'Tab',
                    keyCode: 9,
                    which: 9,
                    bubbles: true
                });
                document.dispatchEvent(tabEvent);
            }
        }, 5000 + Math.random() * 10000);
    }
    
    // ========== 焦点事件 ==========
    function simulateFocusEvents() {
        window.addEventListener('blur', () => {
            // 模拟用户切换标签页后回来
            setTimeout(() => {
                window.focus();
            }, 1000 + Math.random() * 3000);
        });
    }
    
    // ========== 初始化 ==========
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            simulateMouseMove();
            simulateScrolling();
            simulateKeyboardEvents();
            simulateFocusEvents();
        });
    } else {
        simulateMouseMove();
        simulateScrolling();
        simulateKeyboardEvents();
        simulateFocusEvents();
    }
    
    // ========== 页面可见性 ==========
    Object.defineProperty(document, 'hidden', {
        get: () => false,
        configurable: true
    });
    
    Object.defineProperty(document, 'visibilityState', {
        get: () => 'visible',
        configurable: true
    });
    
})();

