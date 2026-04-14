document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    
    if (!token) {
        window.location.href = '/';
        return;
    }

    document.getElementById('user-name').textContent = username;
    document.getElementById('user-avatar').textContent = username.charAt(0).toUpperCase();

    const alertBox = document.getElementById('alert-box');
    const tbody = document.getElementById('files-table-body');
    const emptyState = document.getElementById('empty-state');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const shareModal = document.getElementById('share-modal');

    const showAlert = (msg, type = 'error') => {
        alertBox.className = `mb-4 p-4 rounded-lg text-sm block ${type === 'error' ? 'bg-red-50 text-red-600 border border-red-200' : 'bg-green-50 text-green-600 border border-green-200'}`;
        alertBox.textContent = msg;
        setTimeout(() => { alertBox.classList.add('hidden'); alertBox.classList.remove('block'); }, 4000);
    };

    document.getElementById('btn-logout').addEventListener('click', () => {
        localStorage.clear();
        window.location.href = '/';
    });

    document.getElementById('btn-upload-trigger').addEventListener('click', () => {
        dropZone.classList.toggle('hidden');
    });

    const loadFiles = async () => {
        try {
            const res = await fetch('/api/files', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.status === 401) {
                localStorage.clear();
                window.location.href = '/';
                return;
            }
            const files = await res.json();
            renderFiles(files);
        } catch (err) {
            showAlert('Failed to load files.');
        }
    };

    const formatBytes = (bytes, decimals = 2) => {
        if (!+bytes) return '0 Bytes';
        const k = 1024, dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
    };

    const renderFiles = (files) => {
        tbody.innerHTML = '';
        if (files.length === 0) {
            emptyState.classList.remove('hidden');
            emptyState.classList.add('flex');
            return;
        }
        emptyState.classList.add('hidden');
        emptyState.classList.remove('flex');

        files.forEach(file => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-gray-50 transition-colors group';
            
            const isOwner = file.owner === username;
            
            tr.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <svg class="w-6 h-6 text-blue-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>
                        <div class="text-sm font-medium text-gray-900">${file.filename}</div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${isOwner ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}">
                        ${isOwner ? 'Me' : file.owner}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${formatBytes(file.metadata.size)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${new Date(file.metadata.timestamp).toLocaleDateString()}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                    <button class="text-blue-600 hover:text-blue-900 mx-2 read-btn" data-id="${file._id}">Read</button>
                    <button class="text-indigo-600 hover:text-indigo-900 mx-2 dl-btn" data-id="${file._id}">Download</button>
                    ${isOwner ? `<button class="text-green-600 hover:text-green-900 mx-2 share-btn" data-id="${file._id}">Share</button>
                    <button class="text-red-600 hover:text-red-900 mx-2 del-btn" data-id="${file._id}">Delete</button>` : ''}
                </td>
            `;
            tbody.appendChild(tr);
        });

        document.querySelectorAll('.dl-btn').forEach(b => b.addEventListener('click', async (e) => {
            const id = e.target.getAttribute('data-id');
            try{
                const res = await fetch(`/api/download/${id}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if(!res.ok) {
                    const err = await res.json();
                    showAlert(err.message);
                    return;
                }
                const blob = await res.blob();
                const disposition = res.headers.get('Content-Disposition');
                let filename = 'download';
                if (disposition && disposition.indexOf('attachment') !== -1) {
                    const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                    const matches = filenameRegex.exec(disposition);
                    if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
                }
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            } catch(e) { showAlert('Download failed'); }
        }));

        document.querySelectorAll('.read-btn').forEach(b => b.addEventListener('click', async (e) => {
            const id = e.target.getAttribute('data-id');
            try {
                const res = await fetch(`/api/read/${id}`, { headers: { 'Authorization': `Bearer ${token}` } });
                if (res.ok) {
                    const blob = await res.blob();
                    const url = URL.createObjectURL(blob);
                    window.open(url, '_blank');
                } else {
                    const txt = await res.json();
                    showAlert(txt.message || 'Cannot read file');
                }
            } catch(e) { showAlert('Error reading file'); }
        }));

        document.querySelectorAll('.del-btn').forEach(b => b.addEventListener('click', async (e) => {
            if(!confirm('Delete this file?')) return;
            const id = e.target.getAttribute('data-id');
            const res = await fetch(`/api/delete/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if(res.ok) {
                showAlert('File deleted', 'success');
                loadFiles();
            } else showAlert('Failed to delete');
        }));

        document.querySelectorAll('.share-btn').forEach(b => b.addEventListener('click', (e) => {
            const id = e.target.getAttribute('data-id');
            document.getElementById('share-file-id').value = id;
            document.getElementById('share-username').value = '';
            shareModal.classList.remove('hidden');
        }));
    };

    document.getElementById('btn-cancel-share').addEventListener('click', () => {
        shareModal.classList.add('hidden');
    });

    document.getElementById('btn-confirm-share').addEventListener('click', async () => {
        const id = document.getElementById('share-file-id').value;
        const targetUser = document.getElementById('share-username').value;
        if(!targetUser) return;

        const res = await fetch('/api/share', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ file_id: id, share_with: targetUser })
        });
        const data = await res.json();
        if(res.ok) {
            shareModal.classList.add('hidden');
            showAlert('File shared securely!', 'success');
            loadFiles();
        } else {
            showAlert(data.message);
        }
    });

    const handleUpload = async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const res = await fetch('/api/upload', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });
            const data = await res.json();
            if(res.ok) {
                showAlert('File encrypted and uploaded!', 'success');
                dropZone.classList.add('hidden');
                loadFiles();
            } else {
                showAlert(data.message);
            }
        } catch(err) {
            showAlert('Upload error occurred');
        }
    };

    fileInput.addEventListener('change', (e) => {
        if(e.target.files.length > 0) {
            handleUpload(e.target.files[0]);
            fileInput.value = '';
        }
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('bg-blue-100', 'border-blue-500');
    });
    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('bg-blue-100', 'border-blue-500');
    });
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('bg-blue-100', 'border-blue-500');
        if(e.dataTransfer.files.length > 0) {
            handleUpload(e.dataTransfer.files[0]);
        }
    });

    loadFiles();
});
