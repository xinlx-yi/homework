// 全域變數
let currentView = 'certifications';
let currentCertId = null;
let currentCourseId = null;

// DOM 元素
const certList = document.getElementById('certList');
const courseList = document.getElementById('courseList');
const moduleList = document.getElementById('moduleList');
const certSection = document.querySelector('.certifications');
const coursesSection = document.getElementById('coursesSection');
const modulesSection = document.getElementById('modulesSection');
const backToCerts = document.getElementById('backToCerts');
const backToCourses = document.getElementById('backToCourses');
const detailTitle = document.getElementById('detailTitle');
const detailDescription = document.getElementById('detailDescription');
const detailLink = document.getElementById('detailLink');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    loadCertifications();
    setupEventListeners();
});

// 設定事件監聽器
function setupEventListeners() {
    backToCerts.addEventListener('click', showCertifications);
    backToCourses.addEventListener('click', () => showCourses(currentCertId));
}

// 載入認證列表
async function loadCertifications() {
    try {
        const response = await fetch('/api/certifications');
        const certifications = await response.json();
        
        displayCertifications(certifications);
    } catch (error) {
        console.error('載入認證失敗:', error);
        certList.innerHTML = '<div class="error">載入失敗，請重新整理頁面</div>';
    }
}

// 顯示認證列表
function displayCertifications(certifications) {
    certList.innerHTML = '';
    
    if (certifications.length === 0) {
        certList.innerHTML = '<div class="no-data">目前沒有認證資料</div>';
        return;
    }
    
    certifications.forEach(cert => {
        const certItem = document.createElement('div');
        certItem.className = 'cert-item';
        certItem.innerHTML = `
            <div class="item-title">${cert.title}</div>
            <div class="item-description">${cert.description || '暫無描述'}</div>
        `;
        
        certItem.addEventListener('click', () => {
            selectCertification(cert);
            showCourses(cert.id);
        });
        
        certList.appendChild(certItem);
    });
}

// 選擇認證
function selectCertification(cert) {
    // 移除其他選中狀態
    document.querySelectorAll('.cert-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // 添加選中狀態
    event.currentTarget.classList.add('active');
    
    // 更新詳細資訊
    updateDetailPanel(cert.title, cert.description, cert.url);
    
    currentCertId = cert.id;
}

// 顯示課程列表
async function showCourses(certId) {
    try {
        const response = await fetch(`/api/courses/${certId}`);
        const courses = await response.json();
        
        displayCourses(courses);
        
        // 切換顯示區域
        certSection.style.display = 'none';
        coursesSection.style.display = 'block';
        modulesSection.style.display = 'none';
        
        currentView = 'courses';
    } catch (error) {
        console.error('載入課程失敗:', error);
        courseList.innerHTML = '<div class="error">載入課程失敗</div>';
    }
}

// 顯示課程
function displayCourses(courses) {
    courseList.innerHTML = '';
    
    if (courses.length === 0) {
        courseList.innerHTML = '<div class="no-data">此認證目前沒有相關課程</div>';
        return;
    }
    
    courses.forEach(course => {
        const courseItem = document.createElement('div');
        courseItem.className = 'course-item';
        courseItem.innerHTML = `
            <div class="item-title">${course.title}</div>
            <div class="item-description">${course.description || '暫無描述'}</div>
        `;
        
        courseItem.addEventListener('click', () => {
            selectCourse(course);
            showModules(course.id);
        });
        
        courseList.appendChild(courseItem);
    });
}

// 選擇課程
function selectCourse(course) {
    // 移除其他選中狀態
    document.querySelectorAll('.course-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // 添加選中狀態
    event.currentTarget.classList.add('active');
    
    // 更新詳細資訊
    updateDetailPanel(course.title, course.description, course.url);
    
    currentCourseId = course.id;
}

// 顯示模組列表
async function showModules(courseId) {
    try {
        const response = await fetch(`/api/modules/${courseId}`);
        const modules = await response.json();
        
        displayModules(modules);
        
        // 切換顯示區域
        certSection.style.display = 'none';
        coursesSection.style.display = 'none';
        modulesSection.style.display = 'block';
        
        currentView = 'modules';
    } catch (error) {
        console.error('載入模組失敗:', error);
        moduleList.innerHTML = '<div class="error">載入模組失敗</div>';
    }
}

// 顯示模組
function displayModules(modules) {
    moduleList.innerHTML = '';
    
    if (modules.length === 0) {
        moduleList.innerHTML = '<div class="no-data">此課程目前沒有相關模組</div>';
        return;
    }
    
    modules.forEach(module => {
        const moduleItem = document.createElement('div');
        moduleItem.className = 'module-item';
        moduleItem.innerHTML = `
            <div class="item-title">${module.title}</div>
            <div class="item-description">${module.description || '暫無描述'}</div>
        `;
        
        moduleItem.addEventListener('click', () => {
            selectModule(module);
        });
        
        moduleList.appendChild(moduleItem);
    });
}

// 選擇模組
function selectModule(module) {
    // 移除其他選中狀態
    document.querySelectorAll('.module-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // 添加選中狀態
    event.currentTarget.classList.add('active');
    
    // 更新詳細資訊
    updateDetailPanel(module.title, module.description, module.url);
}

// 顯示認證頁面
function showCertifications() {
    certSection.style.display = 'block';
    coursesSection.style.display = 'none';
    modulesSection.style.display = 'none';
    
    currentView = 'certifications';
    
    // 重置詳細資訊面板
    updateDetailPanel('選擇項目查看詳細資訊', '點擊左側項目來查看詳細說明', null);
}

// 更新詳細資訊面板
function updateDetailPanel(title, description, url) {
    detailTitle.textContent = title;
    detailDescription.textContent = description || '暫無詳細描述';
    
    if (url && url !== '#' && url !== '') {
        detailLink.href = url;
        detailLink.style.display = 'inline-block';
    } else {
        detailLink.style.display = 'none';
    }
}

// 工具函數：顯示載入狀態
function showLoading(container) {
    container.innerHTML = '<div class="loading">載入中...</div>';
}

// 工具函數：顯示錯誤訊息
function showError(container, message) {
    container.innerHTML = `<div class="error">${message}</div>`;
}

// 工具函數：截斷文字
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}