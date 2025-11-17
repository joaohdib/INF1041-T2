import { api } from './api.js';

const broadcastChannel = new BroadcastChannel('plano_app_channel');

document.addEventListener('DOMContentLoaded', () => {
    
    // --- Elementos do DOM ---
    const saldoEl = document.getElementById('saldo-atual');
    const receitasEl = document.getElementById('receitas-mes');
    const despesasEl = document.getElementById('despesas-mes');
    
    const btnVerInbox = document.getElementById('btn-ver-inbox');
    const btnCriarMeta = document.getElementById('btn-criar-meta');
    const btnAddTransacao = document.getElementById('btn-add-transacao');
    
    // Elementos do Modal
    const modalBackdrop = document.getElementById('modal-backdrop');
    const formAddTransacao = document.getElementById('form-add-transacao');
    const btnCancelarModal = document.getElementById('btn-cancelar-modal');
    const btnTipoDespesa = document.getElementById('btn-tipo-despesa');
    const btnTipoReceita = document.getElementById('btn-tipo-receita');
    const inputData = document.getElementById('transacao-data');
    
    // Elementos "Mais Detalhes"
    const detalhesToggle = document.getElementById('mais-detalhes-toggle');
    const detalhesContent = document.getElementById('detalhes-opcionais-content');
    const categoriaSelect = document.getElementById('transacao-categoria');
    const perfilSelect = document.getElementById('transacao-perfil');
    const anexoInput = document.getElementById('transacao-anexo');

    let tipoTransacaoAtual = 'DESPESA';

    // --- Funções ---

    function formatarMoeda(valor) {
        return (valor || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }

    function getHojeFormatado() {
        const hoje = new Date();
        hoje.setMinutes(hoje.getMinutes() - hoje.getTimezoneOffset());
        return hoje.toISOString().split('T')[0];
    }

    async function carregarDashboard() {
        try {
            const stats = await api.getDashboardStats();
            saldoEl.textContent = formatarMoeda(stats.saldo_atual);
            receitasEl.textContent = formatarMoeda(stats.receitas_mes);
            despesasEl.textContent = formatarMoeda(stats.despesas_mes);
        } catch (error) {
            console.error(error);
            alert('Não foi possível carregar o dashboard.');
        }
    }

    async function carregarDropdownsModal() {
        try {
            const [categorias, perfis] = await Promise.all([
                api.getCategorias(),
                api.getPerfis()
            ]);
            
            // Popula Categorias
            categoriaSelect.innerHTML = '<option value="">Selecione uma categoria (opcional)</option>';
            categorias.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id;
                option.textContent = cat.nome;
                categoriaSelect.appendChild(option);
            });

            // Popula Perfis
            perfilSelect.innerHTML = '<option value="">Selecione um perfil (opcional)</option>';
            perfis.forEach(p => {
                const option = document.createElement('option');
                option.value = p.id;
                option.textContent = p.nome;
                perfilSelect.appendChild(option);
            });

        } catch (error) {
            console.error('Falha ao carregar dropdowns', error);
        }
    }

    // --- Funções de Modal ---
    function abrirModal() {
        formAddTransacao.reset(); 
        inputData.value = getHojeFormatado(); 
        tipoTransacaoAtual = 'DESPESA';
        btnTipoDespesa.classList.add('active');
        btnTipoReceita.classList.remove('active');
        
        // --- Reseta o accordion ---
        detalhesContent.classList.add('hidden');
        detalhesToggle.classList.remove('open');
        
        modalBackdrop.classList.remove('hidden');
        carregarDropdownsModal(); 
    }

    function fecharModal() {
        modalBackdrop.classList.add('hidden');
    }


    /** Lida com o envio do formulário de transação */
    async function handleLancarTransacao(event) {
        event.preventDefault();
        
        // --- Usa FormData para incluir arquivos ---
        const formData = new FormData();
        
        const valor = document.getElementById('transacao-valor').value;
        const data = inputData.value;
        
        if (!valor || parseFloat(valor) <= 0) {
            alert('Por favor, insira um valor válido.');
            return;
        }
        if (!data) {
            alert('Por favor, selecione uma data.');
            return;
        }

        // Adiciona campos obrigatórios
        formData.append('valor', parseFloat(valor));
        formData.append('tipo', tipoTransacaoAtual);
        formData.append('data', new Date(data).toISOString());
        
        // Adiciona campos opcionais
        formData.append('descricao', document.getElementById('transacao-descricao').value || '');
        formData.append('id_categoria', document.getElementById('transacao-categoria').value || '');
        formData.append('id_perfil', document.getElementById('transacao-perfil').value || '');
        
        // Adiciona o anexo (se existir)
        const anexoFile = anexoInput.files[0];
        if (anexoFile) {
            formData.append('anexo', anexoFile);
        }

        try {
            
            const transacaoCriada = await api.lancarTransacao(formData);
            fecharModal();

            if (transacaoCriada.status === 'PROCESSADO') {
                alert('Transação lançada e processada!');
                carregarDashboard(); 
            } else {
                alert('Transação lançada! Verifique sua Inbox para categorizar.');
            }

        } catch (error) {
            console.error(error);
            alert('Erro ao lançar transação.');
        }
    }

    // --- Event Listeners ---
    
    btnVerInbox.addEventListener('click', () => {
        window.location.href = 'inbox.html'; 
    });

    if (btnCriarMeta) {
        btnCriarMeta.addEventListener('click', () => {
            window.location.href = 'metas.html';
        });
    }

    // Modal
    btnAddTransacao.addEventListener('click', abrirModal);
    btnCancelarModal.addEventListener('click', fecharModal);
    modalBackdrop.addEventListener('click', (e) => {
        if (e.target === modalBackdrop) fecharModal();
    });
    
    // --- Toggle "Mais Detalhes" ---
    detalhesToggle.addEventListener('click', () => {
        detalhesContent.classList.toggle('hidden');
        detalhesToggle.classList.toggle('open');
    });

    // Toggle Despesa/Receita
    btnTipoDespesa.addEventListener('click', () => {
        tipoTransacaoAtual = 'DESPESA';
        btnTipoDespesa.classList.add('active');
        btnTipoReceita.classList.remove('active');
    });
    btnTipoReceita.addEventListener('click', () => {
        tipoTransacaoAtual = 'RECEITA';
        btnTipoReceita.classList.add('active');
        btnTipoDespesa.classList.remove('active');
    });

    formAddTransacao.addEventListener('submit', handleLancarTransacao);

    // --- Inicialização ---
    carregarDashboard();
    
    // --- Listener para atualização do dashboard ---
    broadcastChannel.onmessage = (event) => {
        if (event.data === 'atualizar_dashboard') {
            console.log("Recebido evento para atualizar dashboard!");
            carregarDashboard();
        }
    };

});
