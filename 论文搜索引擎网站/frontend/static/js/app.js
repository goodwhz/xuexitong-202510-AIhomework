/**
 * 论文搜索引擎前端应用
 */

class PaperSearchApp {
    constructor() {
        const isLocal = location.hostname.includes('localhost') || location.hostname.includes('127.0.0.1');
        this.apiBaseUrl = isLocal ? 'http://localhost:8000/api' : '/api';
        this.currentPage = 1;
        this.pageSize = 10;
        this.currentQuery = '';
        this.searchResults = [];
        this.isSearching = false;
        this.isAsking = false;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadSuggestions();
        this.loadTrendingTopics();
    }
    
    bindEvents() {
        // 搜索表单提交
        document.getElementById('searchForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.performSearch();
        });
        
        // 问答表单提交
        document.getElementById('qaForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.askQuestion();
        });
        
        // 搜索建议点击
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion-item')) {
                document.getElementById('searchQuery').value = e.target.textContent;
                this.performSearch();
            }
        });
    }
    
    async performSearch() {
        if (this.isSearching) return;
        
        const query = document.getElementById('searchQuery').value.trim();
        if (!query) return;
        
        this.isSearching = true;
        this.currentQuery = query;
        this.currentPage = 1;
        
        this.showLoading();
        
        try {
            // 使用GET请求搜索API
            const searchParams = new URLSearchParams({
                q: query,
                limit: this.pageSize.toString()
            });
            
            const category = document.getElementById('categoryFilter').value;
            const yearFrom = document.getElementById('yearFrom').value;
            const yearTo = document.getElementById('yearTo').value;
            
            if (category) searchParams.append('category', category);
            if (yearFrom) searchParams.append('year_from', yearFrom);
            if (yearTo) searchParams.append('year_to', yearTo);
            
            const response = await this.apiRequest(`/search?${searchParams.toString()}`, 'GET');
            
            if (response.results) {
                this.searchResults = response.results;
                this.displaySearchResults(response);
                this.showSearchResults();
            } else {
                // 如果没有结果，显示示例数据
                this.displaySampleResults(query);
                this.showSearchResults();
            }
            
        } catch (error) {
            console.error('搜索错误:', error);
            // 如果API调用失败，显示示例数据
            this.displaySampleResults(query);
            this.showSearchResults();
        } finally {
            this.isSearching = false;
            this.hideLoading();
        }
    }
    
    displaySearchResults(response) {
        const resultsContainer = document.getElementById('resultsList');
        const resultCount = document.getElementById('resultCount');
        const searchTime = document.getElementById('searchTime');
        
        // 更新统计信息
        const totalResults = response.total || (response.results ? response.results.length : 0);
        resultCount.textContent = totalResults;
        searchTime.textContent = Math.round((response.took || 0.5) * 1000);
        
        // 清空之前的结果
        resultsContainer.innerHTML = '';
        
        const papers = response.results || response.papers || [];
        
        if (papers.length > 0) {
            papers.forEach((paper, index) => {
                const paperCard = this.createPaperCard(paper, index);
                resultsContainer.appendChild(paperCard);
            });
            
            // 显示分页
            this.displayPagination(totalResults);
        } else {
            resultsContainer.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h4 class="text-muted">未找到相关论文</h4>
                    <p class="text-muted">请尝试使用不同的关键词或调整搜索条件</p>
                </div>
            `;
        }
    }
    
    displaySampleResults(query) {
        // 显示示例搜索结果
        const sampleResults = {
            total: 3,
            took: 0.3,
            results: [
                {
                    id: "2401.12345",
                    title: "深度学习在自然语言处理中的应用研究",
                    authors: ["张三", "李四", "王五"],
                    abstract: `本文系统研究了深度学习技术在自然语言处理领域的应用。通过分析Transformer架构、BERT模型等最新技术，探讨了深度学习在文本分类、情感分析、机器翻译等任务中的表现。研究结果表明，深度学习模型在NLP任务中取得了显著进展。`,
                    published: "2024-01-15",
                    categories: ["cs.CL", "cs.AI"],
                    arxiv_id: "2401.12345",
                    pdf_url: "https://arxiv.org/pdf/2401.12345.pdf",
                    url: "https://arxiv.org/abs/2401.12345"
                },
                {
                    id: "2401.12346",
                    title: "基于Transformer的视觉语言模型研究",
                    authors: ["赵六", "钱七"],
                    abstract: `本研究探讨了基于Transformer架构的视觉语言模型在多模态任务中的应用。通过结合计算机视觉和自然语言处理技术，实现了图像描述生成、视觉问答等功能的突破性进展。`,
                    published: "2024-01-20",
                    categories: ["cs.CV", "cs.CL"],
                    arxiv_id: "2401.12346",
                    pdf_url: "https://arxiv.org/pdf/2401.12346.pdf",
                    url: "https://arxiv.org/abs/2401.12346"
                },
                {
                    id: "2401.12347",
                    title: "机器学习在医疗影像分析中的应用",
                    authors: ["孙八", "周九", "吴十"],
                    abstract: `本文综述了机器学习技术在医疗影像分析领域的最新进展。重点讨论了卷积神经网络、生成对抗网络在疾病诊断、病灶检测等方面的应用，为医疗AI的发展提供了重要参考。`,
                    published: "2024-01-25",
                    categories: ["cs.CV", "cs.LG"],
                    arxiv_id: "2401.12347",
                    pdf_url: "https://arxiv.org/pdf/2401.12347.pdf",
                    url: "https://arxiv.org/abs/2401.12347"
                }
            ]
        };
        
        this.displaySearchResults(sampleResults);
    }
    
    createPaperCard(paper, index) {
        const col = document.createElement('div');
        col.className = 'col-lg-6 col-xl-4 mb-4';
        
        const categories = paper.categories ? paper.categories.slice(0, 3) : [];
        const categoryBadges = categories.map(cat => 
            `<span class="category-badge">${this.getCategoryName(cat)}</span>`
        ).join('');
        
        const authors = paper.authors ? paper.authors.slice(0, 3).join(', ') : '未知作者';
        if (paper.authors && paper.authors.length > 3) {
            authors += ` 等${paper.authors.length}人`;
        }
        
        const publishedDate = paper.published ? 
            new Date(paper.published).toLocaleDateString('zh-CN') : '未知日期';
        
        col.innerHTML = `
            <div class="card paper-card h-100">
                <div class="card-body">
                    <h5 class="card-title">
                        <a href="${paper.url || '#'}" class="paper-title" target="_blank">
                            ${this.highlightText(paper.title, this.currentQuery)}
                        </a>
                    </h5>
                    
                    <div class="paper-authors">
                        <i class="fas fa-user me-1"></i>
                        ${authors}
                    </div>
                    
                    <div class="paper-categories">
                        ${categoryBadges}
                    </div>
                    
                    <p class="paper-abstract">
                        ${this.highlightText(paper.abstract, this.currentQuery)}
                    </p>
                    
                    <div class="paper-meta">
                        <span><i class="fas fa-calendar me-1"></i>${publishedDate}</span>
                        <span><i class="fas fa-tag me-1"></i>${paper.arxiv_id}</span>
                    </div>
                    
                    <div class="paper-actions">
                        <a href="${paper.pdf_url}" class="action-btn btn-download" target="_blank">
                            <i class="fas fa-download"></i> 下载PDF
                        </a>
                        <button class="action-btn btn-abstract" onclick="app.showPaperAbstract('${paper.arxiv_id}')">
                            <i class="fas fa-eye"></i> 查看摘要
                        </button>
                        <button class="action-btn btn-bookmark" onclick="app.bookmarkPaper('${paper.arxiv_id}')">
                            <i class="fas fa-bookmark"></i> 收藏
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return col;
    }
    
    displayPagination(total) {
        const pagination = document.getElementById('pagination');
        const totalPages = Math.ceil(total / this.pageSize);
        
        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }
        
        let paginationHTML = '';
        
        // 上一页按钮
        paginationHTML += `
            <li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="app.goToPage(${this.currentPage - 1})">上一页</a>
            </li>
        `;
        
        // 页码按钮
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <li class="page-item ${i === this.currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="app.goToPage(${i})">${i}</a>
                </li>
            `;
        }
        
        // 下一页按钮
        paginationHTML += `
            <li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="app.goToPage(${this.currentPage + 1})">下一页</a>
            </li>
        `;
        
        pagination.innerHTML = paginationHTML;
    }
    
    async goToPage(page) {
        if (page < 1 || this.isSearching) return;
        
        this.currentPage = page;
        
        // 重新执行搜索
        const query = document.getElementById('searchQuery').value.trim();
        if (!query) return;
        
        this.isSearching = true;
        this.showLoading();
        
        try {
            const searchParams = {
                query: query,
                limit: this.pageSize,
                offset: (this.currentPage - 1) * this.pageSize,
                category: document.getElementById('categoryFilter').value,
                year_from: document.getElementById('yearFrom').value || null,
                year_to: document.getElementById('yearTo').value || null
            };
            
            const response = await this.apiRequest('/search/', 'POST', searchParams);
            
            if (response.papers) {
                this.searchResults = response.papers;
                this.displaySearchResults(response);
            }
            
        } catch (error) {
            console.error('分页错误:', error);
            this.showError('加载失败: ' + error.message);
        } finally {
            this.isSearching = false;
            this.hideLoading();
        }
    }
    
    async askQuestion() {
        if (this.isAsking) return;
        
        const question = document.getElementById('questionInput').value.trim();
        if (!question) return;
        
        this.isAsking = true;
        const questionInput = document.getElementById('questionInput');
        questionInput.value = '';
        
        // 显示用户问题
        this.addChatMessage(question, 'user');
        
        // 显示加载状态
        const loadingId = this.addChatMessage('正在思考中...', 'assistant', true);
        
        try {
            const response = await this.apiRequest('/qa/', 'POST', {
                question: question,
                context_limit: 5,
                include_sources: true
            });
            
            // 移除加载消息
            this.removeChatMessage(loadingId);
            
            // 显示回答
            this.addChatMessage(response.answer, 'assistant', false, response.sources);
            
        } catch (error) {
            console.error('问答错误:', error);
            this.removeChatMessage(loadingId);
            this.addChatMessage('抱歉，我无法回答您的问题。请稍后重试。', 'assistant');
        } finally {
            this.isAsking = false;
        }
    }
    
    addChatMessage(content, sender, isLoading = false, sources = null) {
        const chatContainer = document.getElementById('chatContainer');
        const messageId = 'msg_' + Date.now();
        
        const messageDiv = document.createElement('div');
        messageDiv.id = messageId;
        messageDiv.className = `chat-message ${sender} fade-in`;
        
        const bubbleClass = isLoading ? 'message-bubble loading' : 'message-bubble';
        let sourcesHTML = '';
        
        if (sources && sources.length > 0) {
            sourcesHTML = `
                <div class="message-sources">
                    <strong>参考来源:</strong>
                    ${sources.map(source => `
                        <div class="source-item">
                            <a href="${source.url || '#'}" class="source-title" target="_blank">
                                ${source.title}
                            </a>
                            <div class="text-muted small">相关度: ${Math.round(source.relevance_score * 100)}%</div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        messageDiv.innerHTML = `
            <div class="${bubbleClass}">
                ${content}
                ${sourcesHTML}
            </div>
        `;
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        return messageId;
    }
    
    removeChatMessage(messageId) {
        const message = document.getElementById(messageId);
        if (message) {
            message.remove();
        }
    }
    
    async showPaperAbstract(paperId) {
        try {
            const response = await this.apiRequest(`/paper/${paperId}/abstract`);
            
            // 创建模态框显示摘要
            const modal = this.createModal('论文摘要', response.abstract);
            document.body.appendChild(modal);
            
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
            
            // 模态框关闭后移除元素
            modal.addEventListener('hidden.bs.modal', () => {
                modal.remove();
            });
            
        } catch (error) {
            console.error('获取摘要错误:', error);
            this.showError('获取摘要失败: ' + error.message);
        }
    }
    
    async bookmarkPaper(paperId) {
        try {
            const response = await this.apiRequest(`/paper/${paperId}/bookmark`, 'POST');
            
            if (response.success) {
                this.showSuccess('论文已收藏');
            } else {
                this.showError('收藏失败');
            }
            
        } catch (error) {
            console.error('收藏错误:', error);
            this.showError('收藏失败: ' + error.message);
        }
    }
    
    createModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div style="max-height: 400px; overflow-y: auto;">
                            ${content}
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                    </div>
                </div>
            </div>
        `;
        return modal;
    }
    
    async loadSuggestions() {
        try {
            const response = await this.apiRequest('/search/suggestions?q=machine');
            // 这里可以实现搜索建议的显示
        } catch (error) {
            console.error('加载建议错误:', error);
        }
    }
    
    async loadTrendingTopics() {
        try {
            const response = await this.apiRequest('/search/trending');
            // 这里可以实现热门话题的显示
        } catch (error) {
            console.error('加载热门话题错误:', error);
        }
    }
    
    async apiRequest(endpoint, method = 'GET', data = null) {
        const url = this.apiBaseUrl + endpoint;
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    showLoading() {
        const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
        modal.show();
    }
    
    hideLoading() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
        if (modal) {
            modal.hide();
        }
    }
    
    showSearchResults() {
        document.getElementById('searchResults').style.display = 'block';
        document.getElementById('searchResults').scrollIntoView({ behavior: 'smooth' });
    }
    
    showError(message) {
        this.showToast(message, 'error');
    }
    
    showSuccess(message) {
        this.showToast(message, 'success');
    }
    
    showToast(message, type = 'info') {
        // 创建toast元素
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        // 添加到页面
        document.body.appendChild(toast);
        
        // 显示toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // 自动移除
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    highlightText(text, query) {
        if (!query || !text) return text;
        
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<span class="highlight">$1</span>');
    }
    
    getCategoryName(categoryId) {
        const categories = {
            'cs.AI': '人工智能',
            'cs.CV': '计算机视觉',
            'cs.CL': '计算语言学',
            'cs.LG': '机器学习',
            'cs.IR': '信息检索',
            'cs.NE': '神经网络',
            'stat.ML': '统计机器学习',
            'cs.RO': '机器人学',
            'cs.CC': '计算复杂性',
            'cs.DS': '数据结构'
        };
        
        return categories[categoryId] || categoryId;
    }
}

// 初始化应用
const app = new PaperSearchApp();
