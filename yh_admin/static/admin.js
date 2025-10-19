// Admin Panel JavaScript

// 전역 변수
let currentEditId = null;

// 유틸리티 함수들
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function showLoading(element) {
    element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 로딩 중...';
    element.disabled = true;
}

function hideLoading(element, originalText) {
    element.innerHTML = originalText;
    element.disabled = false;
}

// API 호출 함수들
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API 호출 실패');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// 폼 관련 함수들
function showAddForm() {
    currentEditId = null;
    document.getElementById('modalTitle').textContent = '새 항목 추가';
    document.getElementById('itemForm').reset();
    document.getElementById('formModal').style.display = 'block';
}

function editItem(id) {
    currentEditId = id;
    document.getElementById('modalTitle').textContent = '항목 수정';
    
    // 기존 데이터로 폼 채우기
    const row = document.querySelector(`tr[data-id="${id}"]`);
    if (!row) {
        showNotification('데이터를 찾을 수 없습니다.', 'error');
        return;
    }
    
    const cells = row.querySelectorAll('td');
    const fields = getFormFields();
    
    fields.forEach((field, index) => {
        if (field.name !== 'id') {
            const input = document.getElementById(field.name);
            if (input) {
                input.value = cells[index].textContent.trim() || '';
            }
        }
    });
    
    document.getElementById('formModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('formModal').style.display = 'none';
    currentEditId = null;
}

async function submitForm(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    showLoading(submitBtn);
    
    try {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // 빈 값 제거
        Object.keys(data).forEach(key => {
            if (data[key] === '') {
                delete data[key];
            }
        });
        
        let result;
        if (currentEditId) {
            // 수정
            result = await apiCall(`/api/${getCurrentModelName()}/${currentEditId}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        } else {
            // 추가
            result = await apiCall(`/api/${getCurrentModelName()}`, {
                method: 'POST',
                body: JSON.stringify(data)
            });
        }
        
        closeModal();
        await refreshTable();
        showNotification('성공적으로 저장되었습니다.', 'success');
        
    } catch (error) {
        showNotification('저장 실패: ' + error.message, 'error');
    } finally {
        hideLoading(submitBtn, originalText);
    }
}

async function deleteItem(id) {
    if (!confirm('정말로 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
        return;
    }
    
    try {
        await apiCall(`/api/${getCurrentModelName()}/${id}`, {
            method: 'DELETE'
        });
        
        await refreshTable();
        showNotification('성공적으로 삭제되었습니다.', 'success');
    } catch (error) {
        showNotification('삭제 실패: ' + error.message, 'error');
    }
}

// 테이블 관련 함수들
async function refreshTable() {
    try {
        const items = await apiCall(`/api/${getCurrentModelName()}`);
        updateTable(items);
    } catch (error) {
        showNotification('데이터를 불러오는데 실패했습니다: ' + error.message, 'error');
    }
}

function updateTable(items) {
    const tbody = document.querySelector('#dataTable tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (items.length === 0) {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = getFormFields().length + 1;
        cell.textContent = '데이터가 없습니다.';
        cell.style.textAlign = 'center';
        cell.style.padding = '2rem';
        cell.style.color = '#666';
        row.appendChild(cell);
        tbody.appendChild(row);
        return;
    }
    
    items.forEach(item => {
        const row = document.createElement('tr');
        row.setAttribute('data-id', item.id);
        
        const fields = getFormFields();
        fields.forEach(field => {
            const cell = document.createElement('td');
            cell.textContent = item[field.name] || '-';
            row.appendChild(cell);
        });
        
        const actionsCell = document.createElement('td');
        actionsCell.className = 'actions';
        actionsCell.innerHTML = `
            <button class="btn btn-sm btn-primary" onclick="editItem(${item.id})">
                <i class="fas fa-edit"></i> 수정
            </button>
            <button class="btn btn-sm btn-danger" onclick="deleteItem(${item.id})">
                <i class="fas fa-trash"></i> 삭제
            </button>
        `;
        row.appendChild(actionsCell);
        tbody.appendChild(row);
    });
}

// 검색 기능
function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const rows = document.querySelectorAll('#dataTable tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

// 유틸리티 함수들
function getCurrentModelName() {
    const path = window.location.pathname;
    const match = path.match(/\/admin\/([^\/]+)/);
    return match ? match[1] : '';
}

function getFormFields() {
    // 폼 필드 정보를 동적으로 가져오는 함수
    const form = document.getElementById('itemForm');
    if (!form) return [];
    
    const inputs = form.querySelectorAll('input, select, textarea');
    const fields = [];
    
    inputs.forEach(input => {
        if (input.name && input.name !== 'id') {
            fields.push({
                name: input.name,
                type: input.type
            });
        }
    });
    
    return fields;
}

// 모달 관련 이벤트
function setupModalEvents() {
    // 모달 외부 클릭 시 닫기
    window.onclick = function(event) {
        const modal = document.getElementById('formModal');
        if (event.target === modal) {
            closeModal();
        }
    }
    
    // ESC 키로 모달 닫기
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeModal();
        }
    });
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    setupSearch();
    setupModalEvents();
    
    // 폼 제출 이벤트 리스너
    const form = document.getElementById('itemForm');
    if (form) {
        form.addEventListener('submit', submitForm);
    }
    
    // 새로고침 버튼 이벤트 리스너
    const refreshBtn = document.querySelector('button[onclick="refreshTable()"]');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshTable);
    }
});

// 전역 함수로 노출 (템플릿에서 사용)
window.showAddForm = showAddForm;
window.editItem = editItem;
window.deleteItem = deleteItem;
window.closeModal = closeModal;
window.submitForm = submitForm;
window.refreshTable = refreshTable;
