import { api } from './api.js';

// --- Canal para notificar o dashboard ---
const broadcastChannel = new BroadcastChannel('plano_app_channel');

document.addEventListener('DOMContentLoaded', () => {

    // (Cache e Elementos do DOM)
    let transacoesCache = [];
    const tableBody = document.getElementById('inbox-table-body');
    const selectAllCheckbox = document.getElementById('checkbox-select-all');
    
    // (Botões)
    const btnAbrirFiltros = document.getElementById('btn-abrir-filtros');
    const btnAbrirMassa = document.getElementById('btn-abrir-massa');
    const btnImportarExtrato = document.getElementById('btn-importar-extrato');
    const searchInput = document.getElementById('filtro-descricao-rapido');

    // (Modais e Formulários)
    const modalFiltros = document.getElementById('modal-filtros-backdrop');
    const modalMassa = document.getElementById('modal-massa-backdrop');
    const modalEdit = document.getElementById('modal-edit-backdrop');
    const modalAnexoViewer = document.getElementById('modal-anexo-viewer');
    const modalImportacao = document.getElementById('modal-importacao-extrato');
    
    const formFiltros = document.getElementById('form-filtros');
    const formAplicarMassa = document.getElementById('form-aplicar-massa');
    const formEditTransacao = document.getElementById('form-edit-transacao');
    const formImportacao = document.getElementById('form-importacao-extrato');
    
    // (Modal de Massa)
    const selectCategoriaMassa = document.getElementById('massa-categoria');
    const selectPerfilMassa = document.getElementById('massa-perfil');
    const contadorSelecionados = document.getElementById('contador-selecionados');

    // (Modal de Filtro)
    const btnLimparFiltros = document.getElementById('btn-limpar-filtros');
    const selectFiltroCategoria = document.getElementById('filtro-categoria');
    const selectFiltroPerfil = document.getElementById('filtro-perfil');
    
    // (Modal de Edição)
    const btnCancelarEdit = document.getElementById('btn-cancelar-edit');
    const editId = document.getElementById('edit-transacao-id');
    const editDescricao = document.getElementById('edit-descricao');
    const editCategoria = document.getElementById('edit-categoria');
    const editPerfil = document.getElementById('edit-perfil');
    const editAnexoInput = document.getElementById('edit-anexo');
    
    // (Modal Anexo Viewer)
    const anexoImageViewer = document.getElementById('anexo-image-viewer');
    const btnFecharAnexoViewer = document.getElementById('btn-fechar-anexo-viewer');

    // (Modal Importação)
    const inputArquivoImport = document.getElementById('import-arquivo');
    const selectMapeamento = document.getElementById('select-mapeamento');
    const mappingManualContainer = document.getElementById('mapeamento-manual');
    const mapDataSelect = document.getElementById('map-data');
    const mapValorSelect = document.getElementById('map-valor');
    const mapDescricaoSelect = document.getElementById('map-descricao');
    const checkboxSalvarMapeamento = document.getElementById('checkbox-salvar-mapeamento');
    const nomeMapeamentoInput = document.getElementById('input-nome-mapeamento');
    const btnCancelarImport = document.getElementById('btn-cancelar-import');
    const checkboxSemCabecalho = document.getElementById('checkbox-sem-cabecalho');


    // --- Funções Auxiliares ---
    function formatarMoeda(valor) {
        return (valor || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }
    function formatarData(isoString) {
        if (!isoString) return '—';
        return new Date(isoString).toLocaleDateString('pt-BR', { timeZone: 'UTC' });
    }
    function popularSelect(selectEl, items, placeholder) {
        selectEl.innerHTML = `<option value="">${placeholder}</option>`;
        items.forEach(item => {
            const opt = document.createElement('option');
            opt.value = item.id;
            opt.textContent = item.nome;
            selectEl.appendChild(opt);
        });
    }
    
    /** Notifica o dashboard para atualizar os saldos */
    function notificarAtualizacaoDashboard() {
        broadcastChannel.postMessage('atualizar_dashboard');
    }

    const MAP_HINTS = {
        data: ['data', 'date', 'dt', 'transaction date', 'dt lanc'],
        valor: ['valor', 'value', 'amount', 'vl', 'vl.', 'valor bruto', 'valor liquido'],
        descricao: ['descricao', 'description', 'memo', 'history', 'info', 'historico']
    };

    let colunasCSVDetectadas = [];
    let ultimoArquivoExtensao = null;
    let arquivoSemCabecalho = false;
    let mapeamentosSalvosCache = [];

    /**
     * Renderiza a tabela da Inbox
     */
    async function carregarInbox(params = {}) {
        tableBody.innerHTML = `<tr><td colspan="8" style="text-align: center;">Carregando...</td></tr>`;
        
        try {
            // --- Carrega TODOS por padrão ---
            const transacoes = await api.getInboxFiltrado(params);
            transacoesCache = transacoes; 

            if (transacoes.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="8" style="text-align: center;">Nenhuma transação encontrada.</td></tr>`;
                return;
            }

            tableBody.innerHTML = ''; 
            transacoes.forEach(t => {
                const tr = document.createElement('tr');
                tr.dataset.id = t.id;
                tr.dataset.status = t.status; 

                const catClasse = t.id_categoria ? '' : 'sem-categoria';
                const catTexto = t.id_categoria ? t.id_categoria : 'Sem categoria';
                const perfilClasse = t.id_perfil ? '' : 'sem-perfil';
                const perfilTexto = t.id_perfil ? t.id_perfil : 'Sem perfil';
                const statusClasse = t.status === 'PENDENTE' ? 'status-pendente' : 'status-processado';

                // --- Lógica para Ações (Editar/Deletar) ---
                let acoesHtml = '';
                if (t.status === 'PENDENTE') {
                    acoesHtml = `
                        <button class="btn-acao btn-editar" data-id="${t.id}">Editar</button>
                        <button class="btn-acao btn-deletar" data-id="${t.id}">Deletar</button>
                    `;
                } else {
                    // Se estiver processada, só mostra o ícone de anexo
                    acoesHtml = `
                        <span class="receipt-icon-placeholder" data-transacao-id="${t.id}"></span>
                    `;
                }

                tr.innerHTML = `
                    <td><input type="checkbox" class="checkbox-item" data-id="${t.id}"></td>
                    <td>${formatarData(t.data)}</td>
                    <td>${t.descricao || '—'}</td>
                    <td class="${t.tipo === 'RECEITA' ? 'positivo' : 'negativo'}">
                        ${formatarMoeda(t.valor)}
                    </td>
                    <td><span class="${catClasse}">${catTexto}</span></td>
                    <td><span class="${perfilClasse}">${perfilTexto}</span></td>
                    <td class="${statusClasse}">${t.status}</td>
                    <td>${acoesHtml}</td>
                `;
                tableBody.appendChild(tr);

                // --- Se processada, busca o anexo ---
                if (t.status === 'PROCESSADO') {
                    verificarAnexos(t.id);
                }
            });

        } catch (error) {
            console.error(error);
            tableBody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: red;">Erro ao carregar transações.</td></tr>`;
        }
    }

    /** --- Busca e renderiza o ícone de recibo --- */
    async function verificarAnexos(transacaoId) {
        try {
            const anexos = await api.getAnexos(transacaoId);
            if (anexos.length > 0) {
                const placeholder = document.querySelector(`.receipt-icon-placeholder[data-transacao-id="${transacaoId}"]`);
                if (placeholder) {
                    placeholder.innerHTML = `
                        <span class="receipt-icon" data-anexo-path="${anexos[0].caminho_storage}" title="Ver recibo">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                        </span>
                    `;
                }
            }
        } catch (error) {
            console.error(`Falha ao buscar anexos para ${transacaoId}`, error);
        }
    }


    /** (carregarDropdownsGlobais - idêntica) */
    async function carregarDropdownsGlobais() {
        try {
            const [categorias, perfis] = await Promise.all([
                api.getCategorias(),
                api.getPerfis()
            ]);
            popularSelect(selectCategoriaMassa, categorias, 'Selecione uma categoria *');
            popularSelect(selectFiltroCategoria, categorias, 'Todas as Categorias');
            popularSelect(editCategoria, categorias, 'Selecione uma categoria');
            popularSelect(selectPerfilMassa, perfis, 'Selecione um perfil *');
            popularSelect(selectFiltroPerfil, perfis, 'Todos os Perfis');
            popularSelect(editPerfil, perfis, 'Selecione um perfil');
        } catch (error) {
            console.error('Falha ao carregar dropdowns globais', error);
        }
    }

    function fecharModais() {
        modalFiltros.classList.add('hidden');
        modalMassa.classList.add('hidden');
        modalEdit.classList.add('hidden');
        modalAnexoViewer.classList.add('hidden'); 
        modalImportacao.classList.add('hidden');
    }

    // --- Handlers de Eventos ---

    // (Filtro Rápido, Abrir Filtros, Limpar Filtros, Submit Filtros - idênticos)
    searchInput.addEventListener('input', (e) => {
        const descricao = e.target.value;
        if (descricao.length > 2 || descricao.length === 0) {
            carregarInbox({ descricao: descricao || undefined });
        }
    });
    btnAbrirFiltros.addEventListener('click', () => modalFiltros.classList.remove('hidden'));
    btnLimparFiltros.addEventListener('click', () => {
        formFiltros.reset();
        document.getElementById('filtro-status-todos').checked = true;
        fecharModais();
        carregarInbox(); 
    });
    btnImportarExtrato.addEventListener('click', () => abrirModalImportacao());
    formFiltros.addEventListener('submit', (e) => {
        e.preventDefault();
        const statusRadio = document.querySelector('input[name="filtro_status"]:checked');
        const params = {
            descricao: document.getElementById('filtro-descricao').value,
            data_de: document.getElementById('filtro-data-de').value,
            data_ate: document.getElementById('filtro-data-ate').value,
            valor_min: document.getElementById('filtro-valor-min').value,
            valor_max: document.getElementById('filtro-valor-max').value,
            status: statusRadio ? statusRadio.value : undefined,
            id_categoria: document.getElementById('filtro-categoria').value,
            id_perfil: document.getElementById('filtro-perfil').value,
            sem_categoria: document.getElementById('filtro-sem-categoria').checked || undefined,
            sem_perfil: document.getElementById('filtro-sem-perfil').checked || undefined,
        };
        carregarInbox(params);
        fecharModais();
    });

    // (Abrir e Submit Modal Massa - idênticos, mas com notificação)
    btnAbrirMassa.addEventListener('click', () => {
        const selecionados = getTransacoesSelecionadas();
        if (selecionados.length === 0) {
            alert('Selecione pelo menos uma transação para organizar em massa.');
            return;
        }
        contadorSelecionados.textContent = `${selecionados.length} transações selecionadas.`;
        formAplicarMassa.reset();
        modalMassa.classList.remove('hidden');
    });
    formAplicarMassa.addEventListener('submit', async (e) => {
        e.preventDefault();
        const ids = getTransacoesSelecionadas();
        const id_categoria = selectCategoriaMassa.value;
        const id_perfil = selectPerfilMassa.value;
        if (!id_categoria || !id_perfil) {
            alert('Categoria e Perfil são obrigatórios.');
            return;
        }
        
        // --- Alerta de Confirmação ---
        if (!confirm(`Você está prestes a processar ${ids.length} transações. Esta ação não pode ser desfeita. Deseja continuar?`)) {
            return;
        }
        
        try {
            const resposta = await api.categorizarEmMassa(ids, id_categoria, id_perfil);
            alert(resposta.mensagem);
            fecharModais();
            carregarInbox(); 
            notificarAtualizacaoDashboard(); 
            selectAllCheckbox.checked = false;
        } catch (error) {
            console.error(error);
            alert('Erro ao aplicar em massa.');
        }
    });

    // --- Handlers de Ações da Tabela (Editar/Deletar/Ver Anexo) ---
    tableBody.addEventListener('click', (e) => {
        const target = e.target.closest('button, span.receipt-icon');
        if (!target) return;
        
        const id = target.dataset.id || target.closest('tr').dataset.id;
        
        if (target.classList.contains('btn-editar')) {
            handleAbrirModalEdicao(id);
        }
        if (target.classList.contains('btn-deletar')) {
            handleDeletar(id);
        }
        if (target.classList.contains('receipt-icon')) {
            handleAbrirAnexoViewer(target.dataset.anexoPath);
        }
    });

    // Abre o modal de edição
    function handleAbrirModalEdicao(id) {
        const transacao = transacoesCache.find(t => t.id === id);
        if (!transacao) return;
        
        formEditTransacao.reset();
        editId.value = transacao.id;
        editDescricao.value = transacao.descricao || '';
        editCategoria.value = transacao.id_categoria || '';
        editPerfil.value = transacao.id_perfil || '';
        
        modalEdit.classList.remove('hidden');
    }
    
    // Salva a edição
    formEditTransacao.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const id = editId.value;
        const id_categoria = editCategoria.value || null;
        const id_perfil = editPerfil.value || null;
        
        const payload = {
            descricao: editDescricao.value || null,
            id_categoria: id_categoria,
            id_perfil: id_perfil,
        };

        // --- Alerta de Confirmação ---
        const vaiProcessar = id_categoria && id_perfil;
        if (vaiProcessar) {
            if (!confirm('Você está prestes a processar esta transação. Esta ação não pode ser desfeita. Deseja continuar?')) {
                return;
            }
        }

        try {
            const transacaoAtualizada = await api.atualizarTransacao(id, payload);
            
            // --- Lógica de anexo na edição ---
            const anexoFile = editAnexoInput.files[0];
            if (anexoFile) {
                const anexoFormData = new FormData();
                anexoFormData.append('anexo', anexoFile);
                await api.anexarRecibo(id, anexoFormData);
            }
            
            fecharModais();
            
            if (transacaoAtualizada.status === 'PROCESSADO') {
                notificarAtualizacaoDashboard();
            }
            
            carregarInbox(); 
        } catch (error) {
            alert(`Erro ao salvar: ${error.message}`);
        }
    });

    // Deleta a transação
    async function handleDeletar(id) {
        if (!confirm('Tem certeza que deseja deletar esta transação? Esta ação não pode ser desfeita.')) {
            return;
        }
        try {
            await api.deletarTransacao(id);
            alert('Transação deletada com sucesso.');
            carregarInbox(); 
        } catch (error) {
            alert(`Erro ao deletar: ${error.message}`);
        }
    }
    
    /** --- Abre o visualizador de anexo --- */
    function handleAbrirAnexoViewer(caminho) {
        // TODO: Tratar PDFs. Por enquanto, só imagens.
        const urlCompleta = `${API_URL.replace('/api', '')}/${caminho}`;
        anexoImageViewer.src = urlCompleta;
        modalAnexoViewer.classList.remove('hidden');
    }

    // (Checkbox "Selecionar Todos" e helpers)
    selectAllCheckbox.addEventListener('change', () => {
        const checkboxes = document.querySelectorAll('.checkbox-item');
        checkboxes.forEach(cb => {
            cb.checked = selectAllCheckbox.checked;
        });
    });
    function getTransacoesSelecionadas() {
        const checkboxes = document.querySelectorAll('.checkbox-item:checked');
        return Array.from(checkboxes).map(cb => cb.dataset.id);
    }
    
    // (Fechar modais)
    btnCancelarEdit.addEventListener('click', fecharModais);
    btnFecharAnexoViewer.addEventListener('click', fecharModais);
    document.getElementById('btn-cancelar-massa').addEventListener('click', fecharModais);
    modalFiltros.addEventListener('click', (e) => { if(e.target === modalFiltros) fecharModais() });
    modalMassa.addEventListener('click', (e) => { if(e.target === modalMassa) fecharModais() });
    modalEdit.addEventListener('click', (e) => { if(e.target === modalEdit) fecharModais() });
    modalAnexoViewer.addEventListener('click', (e) => { if(e.target === modalAnexoViewer) fecharModais() });
    btnCancelarImport.addEventListener('click', fecharModais);
    modalImportacao.addEventListener('click', (e) => { if (e.target === modalImportacao) fecharModais(); });
    inputArquivoImport.addEventListener('change', handleArquivoImportacao);
    checkboxSemCabecalho.addEventListener('change', () => {
        arquivoSemCabecalho = checkboxSemCabecalho.checked;
        if (inputArquivoImport.files[0]) {
            lerArquivoParaMapeamento(inputArquivoImport.files[0]);
        }
    });
    selectMapeamento.addEventListener('change', handleSelecaoMapeamentoChange);
    checkboxSalvarMapeamento.addEventListener('change', handleSalvarMapeamentoToggle);
    formImportacao.addEventListener('submit', handleImportacaoExtrato);

    // --- Fluxo de Importação ---

    async function abrirModalImportacao() {
        formImportacao.reset();
        checkboxSalvarMapeamento.checked = false;
        checkboxSalvarMapeamento.disabled = false;
        nomeMapeamentoInput.classList.add('hidden');
        nomeMapeamentoInput.value = '';
        checkboxSemCabecalho.checked = false;
        checkboxSemCabecalho.disabled = false;
        arquivoSemCabecalho = false;
        colunasCSVDetectadas = [];
        ultimoArquivoExtensao = null;
        mappingManualContainer.classList.add('hidden');
        await carregarMapeamentosSalvos();
        modalImportacao.classList.remove('hidden');
    }

    async function carregarMapeamentosSalvos() {
        try {
            const mapeamentos = await api.getMapeamentosImportacao();
            mapeamentosSalvosCache = mapeamentos;
            selectMapeamento.innerHTML = '<option value="">Selecionar mapeamento...</option>';
            mapeamentos.forEach(map => {
                const option = document.createElement('option');
                option.value = map.id;
                option.textContent = map.nome;
                selectMapeamento.appendChild(option);
            });
        } catch (error) {
            console.error('Falha ao carregar mapeamentos', error);
            selectMapeamento.innerHTML = '<option value="">Nenhum mapeamento disponível</option>';
        }
        atualizarVisibilidadeMapeamento();
    }

    function handleSelecaoMapeamentoChange() {
        const mapping = mapeamentosSalvosCache.find((m) => m.id === selectMapeamento.value);
        if (mapping) {
            checkboxSalvarMapeamento.checked = false;
            checkboxSalvarMapeamento.disabled = true;
            nomeMapeamentoInput.classList.add('hidden');
            nomeMapeamentoInput.value = '';
            checkboxSemCabecalho.checked = Boolean(mapping.sem_cabecalho);
            checkboxSemCabecalho.disabled = true;
            arquivoSemCabecalho = checkboxSemCabecalho.checked;
            mappingManualContainer.classList.add('hidden');
        } else {
            checkboxSalvarMapeamento.disabled = ultimoArquivoExtensao !== 'csv';
            checkboxSemCabecalho.disabled = false;
            checkboxSemCabecalho.checked = arquivoSemCabecalho;
            arquivoSemCabecalho = checkboxSemCabecalho.checked;
            if (inputArquivoImport.files[0]) {
                lerArquivoParaMapeamento(inputArquivoImport.files[0]);
            }
            atualizarVisibilidadeMapeamento();
        }
    }

    function handleSalvarMapeamentoToggle() {
        if (checkboxSalvarMapeamento.checked) {
            nomeMapeamentoInput.classList.remove('hidden');
        } else {
            nomeMapeamentoInput.classList.add('hidden');
            nomeMapeamentoInput.value = '';
        }
    }

    function handleArquivoImportacao(event) {
        const file = event.target.files[0];
        arquivoSemCabecalho = checkboxSemCabecalho.checked;
        if (!file) {
            colunasCSVDetectadas = [];
            ultimoArquivoExtensao = null;
            mappingManualContainer.classList.add('hidden');
            atualizarVisibilidadeMapeamento();
            return;
        }
        ultimoArquivoExtensao = getFileExtension(file);
        lerArquivoParaMapeamento(file);
    }

    function lerArquivoParaMapeamento(file) {
        if (file.name.split('.').pop().toLowerCase() !== 'csv') {
            colunasCSVDetectadas = [];
            mappingManualContainer.classList.add('hidden');
            atualizarVisibilidadeMapeamento();
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const texto = e.target.result || '';
            prepararColunasDetectadas(texto);
            atualizarVisibilidadeMapeamento();
        };
        reader.readAsText(file);
    }

    function prepararColunasDetectadas(texto) {
        const linhas = texto
            .split(/\r?\n/)
            .map((linha) => linha.trim())
            .filter((linha) => linha.length > 0);

        if (linhas.length === 0) {
            colunasCSVDetectadas = [];
            mappingManualContainer.classList.add('hidden');
            return;
        }

        const delimitador = detectarDelimitador(linhas[0]);
        const primeiraLinhaCampos = linhas[0].split(delimitador).map((c) => c.replace(/"/g, '').trim());
        const linhaExemplo = (arquivoSemCabecalho ? linhas[0] : linhas[1]) || '';
        const exemplos = linhaExemplo
            .split(delimitador)
            .map((c) => c.replace(/"/g, '').trim());

        colunasCSVDetectadas = primeiraLinhaCampos.map((valor, index) => {
            const exemplo = exemplos[index] || '';
            if (arquivoSemCabecalho) {
                return {
                    key: `__col_${index}`,
                    label: `Coluna ${index + 1}${exemplo ? ` (ex: ${exemplo})` : ''}`,
                    sample: valor
                };
            }
            const nome = valor || `Coluna ${index + 1}`;
            const label = exemplo ? `${nome} (ex: ${exemplo})` : nome;
            return { key: nome, label, sample: exemplo };
        });

        if (colunasCSVDetectadas.length >= 3 && !selectMapeamento.value) {
            popularMapeamentoManual();
        }
    }

    function detectarDelimitador(linha) {
        if (linha.includes(';')) return ';';
        if (linha.includes('\t')) return '\t';
        return ',';
    }

    function popularMapeamentoManual() {
        const selects = [mapDataSelect, mapValorSelect, mapDescricaoSelect];
        selects.forEach((select) => {
            select.innerHTML = '<option value="">Selecione...</option>';
            colunasCSVDetectadas.forEach((coluna) => {
                const option = document.createElement('option');
                option.value = coluna.key;
                option.textContent = coluna.label;
                select.appendChild(option);
            });
        });

        mapDataSelect.value = sugerirColuna('data') || '';
        mapValorSelect.value = sugerirColuna('valor') || '';
        mapDescricaoSelect.value = sugerirColuna('descricao') || '';
    }

    function sugerirColuna(tipo) {
        const hints = MAP_HINTS[tipo] || [];
        for (const coluna of colunasCSVDetectadas) {
            const header = (coluna.label || '').toLowerCase();
            const sample = (coluna.sample || '').toLowerCase();
            if (tipo === 'data') {
                if (pareceData(sample) || header.includes('data')) {
                    return coluna.key;
                }
            } else if (tipo === 'valor') {
                if (pareceNumero(sample) || header.includes('valor')) {
                    return coluna.key;
                }
            } else if (tipo === 'descricao') {
                if (header.includes('descricao') || (!pareceData(sample) && !pareceNumero(sample))) {
                    return coluna.key;
                }
            }

            if (hints.some((hint) => header.includes(hint))) {
                return coluna.key;
            }
        }
        return '';
    }

    function pareceData(texto) {
        return /\d{1,2}[\/-]\d{1,2}[\/-]\d{2,4}/.test(texto) || /\d{4}-\d{2}-\d{2}/.test(texto);
    }

    function pareceNumero(texto) {
        return /^-?\d+([.,]\d+)?$/.test(texto);
    }

    function atualizarVisibilidadeMapeamento() {
        const deveMostrar =
            ultimoArquivoExtensao === 'csv' &&
            !selectMapeamento.value &&
            colunasCSVDetectadas.length >= 3;

        if (deveMostrar) {
            mappingManualContainer.classList.remove('hidden');
        } else {
            mappingManualContainer.classList.add('hidden');
        }

        if (selectMapeamento.value) {
            checkboxSalvarMapeamento.checked = false;
            checkboxSalvarMapeamento.disabled = true;
            nomeMapeamentoInput.classList.add('hidden');
            nomeMapeamentoInput.value = '';
        } else {
            checkboxSalvarMapeamento.disabled = ultimoArquivoExtensao !== 'csv';
            if (checkboxSalvarMapeamento.disabled) {
                checkboxSalvarMapeamento.checked = false;
                nomeMapeamentoInput.classList.add('hidden');
                nomeMapeamentoInput.value = '';
            }
        }
    }

    function getFileExtension(file) {
        const partes = file.name.split('.');
        if (partes.length < 2) return '';
        return partes.pop().toLowerCase();
    }

    async function handleImportacaoExtrato(event) {
        event.preventDefault();
        const arquivo = inputArquivoImport.files[0];
        if (!arquivo) {
            alert('Selecione um arquivo para importar.');
            return;
        }

        const ext = getFileExtension(arquivo);
        const formData = new FormData();
        formData.append('arquivo', arquivo);
        formData.append('sem_cabecalho', checkboxSemCabecalho.checked ? 'true' : 'false');

        const mapeamentoSelecionado = selectMapeamento.value;
        if (mapeamentoSelecionado) {
            formData.append('id_mapeamento', mapeamentoSelecionado);
        } else if (ext === 'csv') {
            const mapping = {
                data: mapDataSelect.value,
                valor: mapValorSelect.value,
                descricao: mapDescricaoSelect.value
            };

            if (!mapping.data || !mapping.valor || !mapping.descricao) {
                alert('Mapeie Data, Valor e Descrição para continuar.');
                return;
            }
            const valoresUnicos = new Set(Object.values(mapping));
            if (valoresUnicos.size < 3) {
                alert('Cada campo deve usar uma coluna diferente.');
                return;
            }

            formData.append('mapeamento_colunas', JSON.stringify(mapping));

            if (checkboxSalvarMapeamento.checked) {
                const nome = nomeMapeamentoInput.value.trim();
                if (!nome) {
                    alert('Informe um nome para salvar o mapeamento.');
                    return;
                }
                formData.append('salvar_mapeamento_nome', nome);
            }
        }

        try {
            const resultado = await api.importarExtrato(formData);
            alert(`Importação concluída! ${resultado.total_importadas} transações foram enviadas para a Inbox.`);
            fecharModais();
            carregarInbox();
            notificarAtualizacaoDashboard();
            if (resultado.mapeamento_salvo_id) {
                await carregarMapeamentosSalvos();
            }
        } catch (error) {
            alert(error.message || 'Erro ao importar extrato.');
        }
    }

    // --- Inicialização ---
    carregarInbox();
    carregarDropdownsGlobais();
});
