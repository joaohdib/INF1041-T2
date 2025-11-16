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
    const checkboxSalvarMapeamento = document.getElementById('checkbox-salvar-mapeamento');
    const nomeMapeamentoInput = document.getElementById('input-nome-mapeamento');
    const btnCancelarImport = document.getElementById('btn-cancelar-import');
    const mappingPreview = document.getElementById('mapping-preview');
    const mappingTable = document.getElementById('mapping-preview-table');
    const mappingTableHead = mappingTable.querySelector('thead');
    const mappingTableBody = mappingTable.querySelector('tbody');
    const mappingAlert = document.getElementById('mapping-alert');
    const btnSubmitImportacao = document.querySelector('#form-importacao-extrato button[type="submit"]');


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
        data: ['data', 'date', 'dt', 'transaction', 'lançamento'],
        valor: ['valor', 'value', 'amount', 'vl', 'debito', 'credito'],
        descricao: ['descricao', 'description', 'memo', 'history', 'info', 'detalhe']
    };
    const REQUIRED_FIELDS = ['data', 'valor', 'descricao'];

    let colunasCSVDetectadas = [];
    let previewLinhas = [];
    let ultimoArquivoExtensao = null;
    let mapeamentosSalvosCache = [];
    let mappingSelecionadoAtual = null;

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
                let acoesHtml = `<button class="btn-acao btn-deletar" data-id="${t.id}">Deletar</button>`;
                if (t.status === 'PENDENTE') {
                    acoesHtml = `
                        <button class="btn-acao btn-editar" data-id="${t.id}">Editar</button>
                    ` + acoesHtml;
                } else {
                    acoesHtml = `
                        <span class="receipt-icon-placeholder" data-transacao-id="${t.id}"></span>
                    ` + acoesHtml;
                }

                const valorNumero = t.valor * (t.tipo === 'DESPESA' ? -1 : 1);
                tr.innerHTML = `
                    <td><input type="checkbox" class="checkbox-item" data-id="${t.id}"></td>
                    <td>${formatarData(t.data)}</td>
                    <td>${t.descricao || '—'}</td>
                    <td class="valor-cell ${t.tipo === 'RECEITA' ? 'positivo' : 'negativo'}">
                        ${formatarMoeda(valorNumero)}
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
    selectMapeamento.addEventListener('change', handleSelecaoMapeamentoChange);
    checkboxSalvarMapeamento.addEventListener('change', handleSalvarMapeamentoToggle);
    formImportacao.addEventListener('submit', handleImportacaoExtrato);

    // --- Fluxo de Importação ---

    async function abrirModalImportacao() {
        formImportacao.reset();
        checkboxSalvarMapeamento.checked = false;
        checkboxSalvarMapeamento.disabled = true;
        nomeMapeamentoInput.classList.add('hidden');
        nomeMapeamentoInput.value = '';
        colunasCSVDetectadas = [];
        previewLinhas = [];
        ultimoArquivoExtensao = null;
        mappingSelecionadoAtual = null;
        mappingPreview.classList.add('hidden');
        mappingTableHead.innerHTML = '';
        mappingTableBody.innerHTML = '';
        mappingAlert.classList.add('hidden');
        btnSubmitImportacao.disabled = true;
        modalImportacao.classList.remove('hidden');
        carregarMapeamentosSalvos();
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
            if (mappingSelecionadoAtual) {
                const stillExists = mapeamentos.find((m) => m.id === mappingSelecionadoAtual.id);
                selectMapeamento.value = stillExists ? mappingSelecionadoAtual.id : '';
                if (!stillExists) {
                    mappingSelecionadoAtual = null;
                }
            } else {
                selectMapeamento.value = '';
            }
        } catch (error) {
            console.error('Falha ao carregar mapeamentos', error);
            selectMapeamento.innerHTML = '<option value="">Nenhum mapeamento disponível</option>';
        }
        atualizarEstadoSalvarMapeamento();
    }

    function handleSelecaoMapeamentoChange() {
        mappingSelecionadoAtual = mapeamentosSalvosCache.find((m) => m.id === selectMapeamento.value) || null;
        aplicarMapeamentoSalvo(mappingSelecionadoAtual);
        atualizarEstadoSalvarMapeamento();
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
        if (!file) {
            limparPreviewImportacao();
            return;
        }
        ultimoArquivoExtensao = getFileExtension(file);
        if (ultimoArquivoExtensao === 'ofx') {
            limparPreviewImportacao();
            btnSubmitImportacao.disabled = false;
            return;
        }
        if (ultimoArquivoExtensao !== 'csv') {
            limparPreviewImportacao();
            alert('Selecione um arquivo CSV válido.');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const texto = e.target.result || '';
            prepararPreviewCSV(texto);
        };
        reader.readAsText(file);
    }

    function limparPreviewImportacao() {
        colunasCSVDetectadas = [];
        previewLinhas = [];
        mappingPreview.classList.add('hidden');
        mappingTableHead.innerHTML = '';
        mappingTableBody.innerHTML = '';
        mappingAlert.classList.add('hidden');
        mappingAlert.innerHTML = '';
        btnSubmitImportacao.disabled = true;
        checkboxSalvarMapeamento.checked = false;
        checkboxSalvarMapeamento.disabled = true;
        nomeMapeamentoInput.classList.add('hidden');
        nomeMapeamentoInput.value = '';
        atualizarEstadoSalvarMapeamento();
    }

    function prepararPreviewCSV(texto) {
        const linhas = texto
            .split(/\r?\n/)
            .map((linha) => linha.trim())
            .filter((linha) => linha.length > 0);

        if (linhas.length === 0) {
            limparPreviewImportacao();
            alert('Arquivo CSV sem dados.');
            return;
        }

        const delimitador = detectarDelimitador(linhas[0]);
        const linhasSeparadas = linhas.map((linha) =>
            linha.split(delimitador).map((c) => c.replace(/"/g, '').trim())
        );

        const totalColunas = Math.max(...linhasSeparadas.map((r) => r.length));
        colunasCSVDetectadas = Array.from({ length: totalColunas }, (_, index) => ({
            key: `__col_${index}`,
            label: `Coluna ${index + 1}`,
            samples: linhasSeparadas.map((linha) => linha[index] || '').filter(Boolean).slice(0, 6),
            mappedType: '',
            selectEl: null,
        }));

        previewLinhas = linhasSeparadas.slice(0, 6);
        mappingPreview.classList.remove('hidden');
        atualizarEstadoSalvarMapeamento();
        renderMappingTable();
    }

    function detectarDelimitador(linha) {
        if (linha.includes(';')) return ';';
        if (linha.includes('\t')) return '\t';
        return ',';
    }

    function renderMappingTable() {
        mappingTableHead.innerHTML = '';
        mappingTableBody.innerHTML = '';

        if (!colunasCSVDetectadas.length) {
            mappingPreview.classList.add('hidden');
            return;
        }

        const headerRow = document.createElement('tr');
        colunasCSVDetectadas.forEach((coluna) => {
            const th = document.createElement('th');
            const select = document.createElement('select');
            select.innerHTML = `
                <option value="">Mapear...</option>
                <option value="data">Data</option>
                <option value="valor">Valor</option>
                <option value="descricao">Descrição</option>
                <option value="ignorar">Ignorar</option>
            `;
            select.value = coluna.mappedType || '';
            select.addEventListener('change', () => {
                coluna.mappedType = select.value;
                validateMapping();
            });
            coluna.selectEl = select;
            th.appendChild(select);
            headerRow.appendChild(th);
        });
        mappingTableHead.appendChild(headerRow);

        previewLinhas.forEach((linha) => {
            const tr = document.createElement('tr');
            colunasCSVDetectadas.forEach((_, index) => {
                const td = document.createElement('td');
                const valor = linha[index] || '';
                td.textContent = valor || '—';
                tr.appendChild(td);
            });
            mappingTableBody.appendChild(tr);
        });

        aplicarMapeamentoSalvo(mappingSelecionadoAtual);
        atualizarEstadoSalvarMapeamento();
        validateMapping();
    }

    function aplicarMapeamentoSalvo(mapping) {
        if (!colunasCSVDetectadas.length) return;

        colunasCSVDetectadas.forEach((coluna) => {
            let novoValor = '';
            if (mapping) {
                if (mapping.coluna_data === coluna.key) novoValor = 'data';
                if (mapping.coluna_valor === coluna.key) novoValor = 'valor';
                if (mapping.coluna_descricao === coluna.key) novoValor = 'descricao';
            } else {
                novoValor = sugerirTipoParaColuna(coluna);
            }
            coluna.mappedType = novoValor;
            if (coluna.selectEl) {
                coluna.selectEl.value = novoValor || '';
            }
        });
    }

    function sugerirTipoParaColuna(coluna) {
        const valores = coluna.samples || [];
        if (valores.some((valor) => pareceData(valor))) return 'data';
        if (valores.some((valor) => pareceNumero(valor))) return 'valor';
        if (valores.length) return 'descricao';
        return '';
    }

    function pareceData(texto) {
        return /\d{1,2}[\/-]\d{1,2}[\/-]\d{2,4}/.test(texto) || /\d{4}-\d{2}-\d{2}/.test(texto);
    }

    function pareceNumero(texto) {
        return /^-?\d+([.,]\d+)?$/.test(texto);
    }

    function validateMapping() {
        if (!colunasCSVDetectadas.length) {
            btnSubmitImportacao.disabled = true;
            clearMappingAlert();
            return;
        }
        const { errors } = coletarMapping(false);
        if (errors.length) {
            showMappingAlert(errors[0]);
            btnSubmitImportacao.disabled = true;
        } else {
            clearMappingAlert();
            btnSubmitImportacao.disabled = false;
        }
    }

    function showMappingAlert(message) {
        mappingAlert.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
            <div>
                <strong>Mapeamento incompleto</strong>
                <p>${message}</p>
            </div>
        `;
        mappingAlert.classList.remove('hidden');
    }

    function clearMappingAlert() {
        mappingAlert.classList.add('hidden');
        mappingAlert.innerHTML = '';
    }

    function coletarMapping(shouldThrow = true) {
        const mapping = {
            data: null,
            valor: null,
            descricao: null,
        };
        const errors = [];

        colunasCSVDetectadas.forEach((coluna) => {
            const tipo = coluna.mappedType;
            if (!tipo || tipo === 'ignorar') return;
            if (!REQUIRED_FIELDS.includes(tipo)) return;

            if (mapping[tipo] && mapping[tipo] !== coluna.key) {
                errors.push(`Você selecionou mais de uma coluna como ${tipo}.`);
            } else {
                mapping[tipo] = coluna.key;
            }
        });

        REQUIRED_FIELDS.forEach((campo) => {
            if (!mapping[campo]) {
                errors.push(`Mapeie a coluna de ${campo}.`);
            }
        });

        if (shouldThrow && errors.length) {
            throw new Error(errors.join(' '));
        }

        return { mapping, errors };
    }

    function atualizarEstadoSalvarMapeamento() {
        if (!colunasCSVDetectadas.length) {
            checkboxSalvarMapeamento.checked = false;
            checkboxSalvarMapeamento.disabled = true;
            nomeMapeamentoInput.classList.add('hidden');
            nomeMapeamentoInput.value = '';
            return;
        }

        if (mappingSelecionadoAtual) {
            checkboxSalvarMapeamento.checked = false;
            checkboxSalvarMapeamento.disabled = true;
            nomeMapeamentoInput.classList.add('hidden');
            nomeMapeamentoInput.value = '';
        } else {
            checkboxSalvarMapeamento.disabled = false;
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

        const mapeamentoSelecionado = selectMapeamento.value;
        if (mapeamentoSelecionado) {
            formData.append('id_mapeamento', mapeamentoSelecionado);
        } else if (ext === 'csv') {
            const { mapping, errors } = coletarMapping(false);
            if (errors.length) {
                showMappingAlert(errors[0]);
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
        } else {
            clearMappingAlert();
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
