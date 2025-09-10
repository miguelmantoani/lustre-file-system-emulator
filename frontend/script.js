document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'http://127.0.0.1:5000';
    const NUM_OSTS = 4; // Deve ser igual ao do backend

    // Elementos da UI
    const fileList = document.getElementById('file-list');
    const currentPathEl = document.getElementById('current-path');
    const detailsContent = document.getElementById('details-content');
    const setLayoutBtn = document.getElementById('set-layout-btn');
    
    // --- NOVOS ELEMENTOS PARA VISUALIZAÇÃO ---
    const vizContainer = document.getElementById('visualization-container');
    const stripeViz = document.getElementById('stripe-visualization');
    
    // Outros elementos (formulários, modais, etc.)
    const uploadForm = document.getElementById('upload-form');
    const createTextFileBtn = document.getElementById('create-text-file-btn');
    const layoutModal = document.getElementById('layout-modal');
    const textFileModal = document.getElementById('text-file-modal');
    // ... (demais constantes para os modais, se necessário)

    let currentPath = '/';
    let selectedItem = null;

    // --- NOVA FUNÇÃO PARA RENDERIZAR O GRÁFICO ---
    function renderVisualization(distribution) {
        stripeViz.innerHTML = ''; // Limpa o conteúdo anterior
        
        if (Object.keys(distribution).length === 0) {
            vizContainer.classList.add('hidden');
            return;
        }

        vizContainer.classList.remove('hidden');

        for (let i = 0; i < NUM_OSTS; i++) {
            const ostName = `ost${i + 1}`;
            const chunks = distribution[ostName] || [];

            const row = document.createElement('div');
            row.className = 'ost-row';

            const label = document.createElement('div');
            label.className = 'ost-label';
            label.textContent = `OST ${i + 1}`;
            
            const bar = document.createElement('div');
            bar.className = 'ost-bar';

            chunks.forEach(chunkIndex => {
                const chunkDiv = document.createElement('div');
                chunkDiv.className = 'chunk';
                chunkDiv.textContent = chunkIndex;
                chunkDiv.title = `Chunk ${chunkIndex}`; // Dica ao passar o mouse
                bar.appendChild(chunkDiv);
            });

            row.appendChild(label);
            row.appendChild(bar);
            stripeViz.appendChild(row);
        }
    }


    async function selectItem(element, path) {
        if (selectedItem && selectedItem.element) {
            selectedItem.element.classList.remove('selected');
        }
        element.classList.add('selected');
        selectedItem = { path, element };
        setLayoutBtn.classList.remove('hidden');

        // Limpa visualização antiga
        renderVisualization({}); 

        // Busca detalhes de texto (getstripe)
        try {
            const response = await fetch(`${API_URL}/api/layout?path=${encodeURIComponent(path)}`);
            const layout = await response.json();
            
            if (response.ok) {
                const sizeInMB = (layout.stripe_size_bytes / (1024 * 1024)).toFixed(2);
                detailsContent.innerHTML = `
                    <p><strong>Caminho:</strong> ${path}</p>
                    <p><strong>Stripe Count:</strong> ${layout.stripe_count}</p>
                    <p><strong>Stripe Size:</strong> ${sizeInMB} MB</p>
                `;

                // --- BUSCA DADOS PARA VISUALIZAÇÃO E RENDERIZA ---
                const vizResponse = await fetch(`${API_URL}/api/files/visualize?path=${encodeURIComponent(path)}`);
                const distribution = await vizResponse.json();
                if (vizResponse.ok) {
                    renderVisualization(distribution);
                }

            } else {
                detailsContent.innerHTML = `<p>Erro ao buscar detalhes: ${layout.error}</p>`;
            }
        } catch (error) {
            detailsContent.innerHTML = `<p>Erro de conexão ao buscar detalhes.</p>`;
        }
    }

    function clearSelection() {
        if (selectedItem && selectedItem.element) {
            selectedItem.element.classList.remove('selected');
        }
        selectedItem = null;
        setLayoutBtn.classList.add('hidden');
        detailsContent.innerHTML = '<p>Selecione um arquivo ou diretório para ver os detalhes.</p>';
        renderVisualization({}); // Limpa/esconde a visualização
    }
    
    // O resto do script.js (fetchFiles, renderFileList, createListItem, e todos os event listeners) continua o mesmo.
    // Cole o resto do seu script.js funcional aqui, sem alterações.
    // ...
    // Vou colar o resto para garantir que esteja completo
    const closeLayoutModalBtn = document.getElementById('close-layout-modal');
    const layoutForm = document.getElementById('layout-form');
    const modalPath = document.getElementById('modal-path');
    const stripeCountInput = document.getElementById('stripe-count');
    const stripeSizeInput = document.getElementById('stripe-size');
    const closeTextFileModalBtn = document.getElementById('close-text-file-modal');
    const createTextForm = document.getElementById('create-text-form');

    async function fetchFiles(path) {
        try {
            const response = await fetch(`${API_URL}/api/files?path=${encodeURIComponent(path)}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Falha ao buscar arquivos');
            }
            const files = await response.json();
            renderFileList(files);
            currentPath = path;
            currentPathEl.textContent = path;
            clearSelection();
        } catch (error) {
            console.error(error);
            alert(error.message);
        }
    }

    function renderFileList(files) {
        fileList.innerHTML = '';
        if (currentPath !== '/') {
            const parentPath = currentPath.substring(0, currentPath.lastIndexOf('/')) || '/';
            const li = document.createElement('li');
            li.innerHTML = `<span class="icon">🔙</span> ..`;
            li.addEventListener('click', () => fetchFiles(parentPath));
            fileList.appendChild(li);
        }
        files.filter(f => f.is_directory).forEach(file => {
            const li = createListItem(file);
            li.addEventListener('dblclick', () => {
                const newPath = `${currentPath}${currentPath.endsWith('/') ? '' : '/'}${file.filename}`.replace('//', '/');
                fetchFiles(newPath);
            });
            fileList.appendChild(li);
        });
        files.filter(f => !f.is_directory).forEach(file => {
            const li = createListItem(file);
            fileList.appendChild(li);
        });
    }

    function createListItem(file) {
        const li = document.createElement('li');
        const icon = file.is_directory ? '📁' : '📄';
        const fullPath = `${currentPath}${currentPath.endsWith('/') ? '' : '/'}${file.filename}`.replace('//', '/');
        li.innerHTML = `<span class="icon">${icon}</span> ${file.filename}`;
        li.dataset.path = fullPath;
        li.dataset.id = file.id;
        li.addEventListener('click', () => selectItem(li, fullPath));
        return li;
    }

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const file = e.target.querySelector('#file-input').files[0];
        if (!file) { alert('Por favor, selecione um arquivo.'); return; }
        const formData = new FormData();
        formData.append('file', file);
        formData.append('path', currentPath);
        try {
            const response = await fetch(`${API_URL}/api/files/upload`, { method: 'POST', body: formData });
            const result = await response.json();
            alert(result.message || result.error);
            if (response.ok) { fetchFiles(currentPath); uploadForm.reset(); }
        } catch (error) { alert('Erro ao enviar o arquivo.'); console.error(error); }
    });

    setLayoutBtn.addEventListener('click', () => {
        if (!selectedItem) return;
        modalPath.textContent = selectedItem.path;
        fetch(`${API_URL}/api/layout?path=${encodeURIComponent(selectedItem.path)}`)
            .then(res => res.json())
            .then(layout => {
                stripeCountInput.value = layout.stripe_count;
                stripeSizeInput.value = layout.stripe_size_bytes / (1024 * 1024);
                layoutModal.classList.remove('hidden');
            });
    });

    closeLayoutModalBtn.addEventListener('click', () => layoutModal.classList.add('hidden'));

    layoutForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = { path: selectedItem.path, stripe_count: stripeCountInput.value, stripe_size_mb: stripeSizeInput.value };
        try {
            const response = await fetch(`${API_URL}/api/layout`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
            const result = await response.json();
            alert(result.message || result.error);
            if (response.ok) { layoutModal.classList.add('hidden'); selectItem(selectedItem.element, selectedItem.path); }
        } catch (error) { alert('Erro ao configurar o layout.'); console.error(error); }
    });
    
    createTextFileBtn.addEventListener('click', () => { createTextForm.reset(); textFileModal.classList.remove('hidden'); });
    closeTextFileModalBtn.addEventListener('click', () => textFileModal.classList.add('hidden'));
    
    createTextForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const filename = e.target.querySelector('#new-filename').value;
        const content = e.target.querySelector('#new-file-content').value;
        if (!filename.trim()) { alert('O nome do arquivo é obrigatório.'); return; }
        const data = { path: currentPath, filename: filename, content: content };
        try {
            const response = await fetch(`${API_URL}/api/files/create`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
            const result = await response.json();
            alert(result.message || result.error);
            if (response.ok) { textFileModal.classList.add('hidden'); fetchFiles(currentPath); }
        } catch (error) { alert('Erro ao criar o arquivo de texto.'); console.error(error); }
    });

    window.addEventListener('click', (e) => {
        if (e.target === layoutModal) layoutModal.classList.add('hidden');
        if (e.target === textFileModal) textFileModal.classList.add('hidden');
    });

    fetchFiles('/');
});