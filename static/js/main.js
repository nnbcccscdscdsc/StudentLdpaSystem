// 学生LDAP系统主要JavaScript功能

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 初始化弹出框
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // 添加页面加载动画
    document.body.classList.add('fade-in');
});

// 通用功能函数
const Utils = {
    // 显示加载状态
    showLoading: function(element) {
        if (element) {
            element.innerHTML = '<span class="loading"></span> 处理中...';
            element.disabled = true;
        }
    },

    // 隐藏加载状态
    hideLoading: function(element, originalText) {
        if (element) {
            element.innerHTML = originalText || '提交';
            element.disabled = false;
        }
    },

    // 显示成功消息
    showSuccess: function(message) {
        this.showAlert(message, 'success');
    },

    // 显示错误消息
    showError: function(message) {
        this.showAlert(message, 'danger');
    },

    // 显示警告消息
    showWarning: function(message) {
        this.showAlert(message, 'warning');
    },

    // 显示信息消息
    showInfo: function(message) {
        this.showAlert(message, 'info');
    },

    // 显示警告框
    showAlert: function(message, type) {
        const alertContainer = document.getElementById('alert-container') || this.createAlertContainer();
        const alertId = 'alert-' + Date.now();
        
        const alertHtml = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${this.getAlertIcon(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('beforeend', alertHtml);
        
        // 自动隐藏警告框
        setTimeout(() => {
            const alertElement = document.getElementById(alertId);
            if (alertElement) {
                const bsAlert = new bootstrap.Alert(alertElement);
                bsAlert.close();
            }
        }, 5000);
    },

    // 创建警告框容器
    createAlertContainer: function() {
        const container = document.createElement('div');
        container.id = 'alert-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    },

    // 获取警告框图标
    getAlertIcon: function(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    },

    // 确认对话框
    confirm: function(message, callback) {
        if (confirm(message)) {
            if (typeof callback === 'function') {
                callback();
            }
        }
    },

    // 格式化日期
    formatDate: function(date) {
        return new Date(date).toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // 防抖函数
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// 学生管理功能
const StudentManager = {
    // 添加学生
    addStudent: function(formData) {
        const submitBtn = document.querySelector('#addStudentModal .btn-success');
        const originalText = submitBtn.innerHTML;
        
        Utils.showLoading(submitBtn);
        
        // 模拟API调用
        setTimeout(() => {
            Utils.hideLoading(submitBtn, originalText);
            Utils.showSuccess('学生添加成功！');
            
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('addStudentModal'));
            modal.hide();
            
            // 刷新页面
            setTimeout(() => {
                location.reload();
            }, 1000);
        }, 2000);
    },

    // 删除学生
    deleteStudent: function(uid) {
        Utils.confirm(`确定要删除学生 ${uid} 吗？此操作不可撤销！`, () => {
            Utils.showInfo('正在删除学生...');
            
            // 模拟API调用
            setTimeout(() => {
                Utils.showSuccess('学生删除成功！');
                setTimeout(() => {
                    location.reload();
                }, 1000);
            }, 1500);
        });
    },

    // 编辑学生
    editStudent: function(uid) {
        Utils.showInfo('编辑功能开发中...');
    },

    // 查看学生详情
    viewStudent: function(uid) {
        Utils.showInfo('查看学生详情：' + uid);
    }
};

// 批量导入功能
const ImportManager = {
    // 提交导入
    submitImport: function() {
        const fileInput = document.getElementById('importFile');
        const file = fileInput.files[0];
        
        if (!file) {
            Utils.showError('请选择要导入的文件！');
            return;
        }
        
        const submitBtn = document.querySelector('#importModal .btn-info');
        const originalText = submitBtn.innerHTML;
        
        Utils.showLoading(submitBtn);
        
        // 模拟文件上传和导入
        setTimeout(() => {
            Utils.hideLoading(submitBtn, originalText);
            Utils.showSuccess('文件导入成功！共导入 5 条记录。');
            
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('importModal'));
            modal.hide();
            
            // 刷新页面
            setTimeout(() => {
                location.reload();
            }, 1000);
        }, 3000);
    },

    // 验证文件格式
    validateFile: function(file) {
        const allowedTypes = [
            'text/csv',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ];
        
        const allowedExtensions = ['.csv', '.xls', '.xlsx'];
        const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
        
        if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
            Utils.showError('不支持的文件格式！请选择CSV或Excel文件。');
            return false;
        }
        
        if (file.size > 10 * 1024 * 1024) { // 10MB
            Utils.showError('文件大小不能超过10MB！');
            return false;
        }
        
        return true;
    }
};

// 搜索功能
const SearchManager = {
    // 初始化搜索
    init: function() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', Utils.debounce(this.search, 300));
        }
    },

    // 执行搜索
    search: function(event) {
        const query = event.target.value.toLowerCase();
        const tableRows = document.querySelectorAll('tbody tr');
        
        tableRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(query)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
};

// 导出功能
const ExportManager = {
    // 导出为CSV
    exportToCSV: function() {
        Utils.showInfo('正在导出CSV文件...');
        
        setTimeout(() => {
            Utils.showSuccess('CSV文件导出成功！');
        }, 2000);
    },

    // 导出为Excel
    exportToExcel: function() {
        Utils.showInfo('正在导出Excel文件...');
        
        setTimeout(() => {
            Utils.showSuccess('Excel文件导出成功！');
        }, 2000);
    }
};

// 全局函数（供HTML调用）
function showAddStudentModal() {
    const modal = new bootstrap.Modal(document.getElementById('addStudentModal'));
    modal.show();
}

function showImportModal() {
    const modal = new bootstrap.Modal(document.getElementById('importModal'));
    modal.show();
}

function submitAddStudent() {
    const form = document.getElementById('addStudentForm');
    const formData = new FormData(form);
    StudentManager.addStudent(formData);
}

function submitImport() {
    const fileInput = document.getElementById('importFile');
    const file = fileInput.files[0];
    
    if (!file) {
        Utils.showError('请选择要导入的文件！');
        return;
    }
    
    if (!ImportManager.validateFile(file)) {
        return;
    }
    
    ImportManager.submitImport();
}

function viewStudent(uid) {
    StudentManager.viewStudent(uid);
}

function editStudent(uid) {
    StudentManager.editStudent(uid);
}

function deleteStudent(uid) {
    StudentManager.deleteStudent(uid);
}

function refreshData() {
    Utils.showInfo('正在刷新数据...');
    setTimeout(() => {
        location.reload();
    }, 1000);
}

function showHelp() {
    const helpContent = `
        <h5>系统帮助</h5>
        <ul>
            <li><strong>添加学生：</strong>点击"添加学生"按钮，填写学生信息</li>
            <li><strong>批量导入：</strong>准备CSV或Excel文件，点击"批量导入"</li>
            <li><strong>学生管理：</strong>在列表中查看、编辑、删除学生信息</li>
            <li><strong>搜索功能：</strong>在搜索框中输入关键词快速查找</li>
        </ul>
        <p class="text-muted">如有其他问题，请联系系统管理员。</p>
    `;
    
    // 创建模态框显示帮助信息
    const modalHtml = `
        <div class="modal fade" id="helpModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-info text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-question-circle me-2"></i>帮助中心
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${helpContent}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 移除已存在的帮助模态框
    const existingModal = document.getElementById('helpModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 添加新的帮助模态框
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // 显示模态框
    const modal = new bootstrap.Modal(document.getElementById('helpModal'));
    modal.show();
}
