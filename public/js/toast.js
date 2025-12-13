/**
 * MeetSpot Toast Notification System
 * 现代化的通知系统，替代 alert()
 *
 * 使用示例:
 * showToast('success', '推荐生成成功！', '已为您找到8个最佳会面点');
 * showToast('error', '请求失败', '请检查网络连接后重试');
 */

class ToastManager {
    constructor() {
        this.container = null;
        this.toasts = new Map();
        this.init();
    }

    init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            this.container.setAttribute('role', 'region');
            this.container.setAttribute('aria-label', '通知消息');
            this.container.setAttribute('aria-live', 'polite');
            document.body.appendChild(this.container);
        }
    }

    /**
     * 显示 Toast 通知
     * @param {string} type - 类型: 'success', 'error', 'info', 'warning'
     * @param {string} title - 标题
     * @param {string} message - 消息内容（可选）
     * @param {number} duration - 显示时长（毫秒），0 表示不自动关闭
     */
    show(type = 'info', title = '', message = '', duration = 5000) {
        const id = Date.now() + Math.random();
        const toast = this.createToast(id, type, title, message);

        this.container.appendChild(toast);
        this.toasts.set(id, toast);

        // 触发进入动画
        requestAnimationFrame(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        });

        // 自动关闭
        if (duration > 0) {
            setTimeout(() => this.dismiss(id), duration);
        }

        return id;
    }

    createToast(id, type, title, message) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.setAttribute('role', 'alert');
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';

        const iconMap = {
            success: 'bx-check-circle',
            error: 'bx-error-circle',
            info: 'bx-info-circle',
            warning: 'bx-error'
        };

        toast.innerHTML = `
            <i class='bx ${iconMap[type]} toast-icon'></i>
            <div class="toast-content">
                <div class="toast-title">${this.escapeHtml(title)}</div>
                ${message ? `<div class="toast-message">${this.escapeHtml(message)}</div>` : ''}
            </div>
            <button
                class="toast-close"
                onclick="toastManager.dismiss(${id})"
                aria-label="关闭通知"
            >
                <i class='bx bx-x'></i>
            </button>
        `;

        return toast;
    }

    dismiss(id) {
        const toast = this.toasts.get(id);
        if (!toast) return;

        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';

        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
            this.toasts.delete(id);
        }, 300);
    }

    dismissAll() {
        this.toasts.forEach((_, id) => this.dismiss(id));
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 全局实例
const toastManager = new ToastManager();

// 便捷函数
function showToast(type, title, message = '', duration = 5000) {
    return toastManager.show(type, title, message, duration);
}

function showSuccess(title, message = '', duration = 5000) {
    return toastManager.show('success', title, message, duration);
}

function showError(title, message = '', duration = 7000) {
    return toastManager.show('error', title, message, duration);
}

function showInfo(title, message = '', duration = 5000) {
    return toastManager.show('info', title, message, duration);
}

function showWarning(title, message = '', duration = 6000) {
    return toastManager.show('warning', title, message, duration);
}

// 导出到全局
window.toastManager = toastManager;
window.showToast = showToast;
window.showSuccess = showSuccess;
window.showError = showError;
window.showInfo = showInfo;
window.showWarning = showWarning;
