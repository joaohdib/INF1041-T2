import { api } from './api.js';

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-criar-meta');
    const feedbackEl = document.getElementById('meta-feedback');
    const sugestoesCard = document.getElementById('meta-sugestoes-card');
    const btnSubmit = document.getElementById('btn-criar-meta');

    const nomeInput = document.getElementById('meta-nome');
    const valorInput = document.getElementById('meta-valor');
    const dataInput = document.getElementById('meta-data');
    const perfilSelect = document.getElementById('meta-perfil');

    const resumoNome = document.getElementById('resumo-nome');
    const resumoValor = document.getElementById('resumo-valor');
    const resumoData = document.getElementById('resumo-data');
    const resumoPerfil = document.getElementById('resumo-perfil');
    const reservaSemanal = document.getElementById('reserva-semanal');
    const reservaMensal = document.getElementById('reserva-mensal');

    const metasContainer = document.getElementById('metas-list');
    const metasEmpty = document.getElementById('metas-empty');
    const btnRecarregarMetas = document.getElementById('btn-recarregar-metas');
    const btnIrCriarMeta = document.getElementById('btn-ir-criar-meta');
    const metasConcluidasCard = document.getElementById('metas-concluidas-card');
    const metasConcluidasContainer = document.getElementById('metas-concluidas');

    const modalReserva = document.getElementById('modal-reserva');
    const modalReservaTitulo = document.getElementById('modal-reserva-titulo');
    const modalReservaMeta = document.getElementById('modal-reserva-meta');
    const formReserva = document.getElementById('form-reserva');
    const inputReservaMetaId = document.getElementById('reserva-meta-id');
    const inputReservaId = document.getElementById('reserva-id');
    const inputReservaValor = document.getElementById('reserva-valor');
    const inputReservaObservacao = document.getElementById('reserva-observacao');
    const btnCancelarReserva = document.getElementById('btn-cancelar-reserva');
    const btnSalvarReserva = document.getElementById('btn-salvar-reserva');

    const modalConfirmReserva = document.getElementById('modal-confirm-reserva');
    const confirmText = document.getElementById('confirm-reserva-text');
    const btnCancelarReservaExclusao = document.getElementById('btn-cancelar-reserva-exclusao');
    const btnConfirmarReservaExclusao = document.getElementById('btn-confirmar-reserva-exclusao');

    const metasState = new Map();
    let reservaModalMode = 'create';
    let reservaParaExcluir = null;

    const currencyFormatter = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
    const dateFormatter = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'medium' });
    const dateTimeFormatter = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' });

    const minDate = new Date();
    minDate.setDate(minDate.getDate() + 1);
    minDate.setMinutes(minDate.getMinutes() - minDate.getTimezoneOffset());
    if (dataInput) {
        dataInput.min = minDate.toISOString().split('T')[0];
        dataInput.value = dataInput.min;
    }

    function resetFeedback() {
        if (!feedbackEl) return;
        feedbackEl.className = 'hidden';
        feedbackEl.textContent = '';
    }

    function showFeedback(message, type) {
        if (!feedbackEl) return;
        feedbackEl.textContent = message;
        feedbackEl.className = `meta-alert meta-alert-${type}`;
    }

    function formatCurrency(value) {
        return currencyFormatter.format(Number(value) || 0);
    }

    function formatDateValue(value) {
        if (!value) return '-';
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return '-';
        return dateFormatter.format(date);
    }

    function formatDateTimeValue(value) {
        if (!value) return 'Data indisponível';
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return 'Data indisponível';
        return dateTimeFormatter.format(date);
    }

    function normalizarReserva(reserva) {
        return {
            id: reserva.id,
            id_meta: reserva.id_meta,
            valor: Number(reserva.valor),
            observacao: reserva.observacao || '',
            criado_em: reserva.criado_em || null,
            atualizado_em: reserva.atualizado_em || null,
        };
    }

    function atualizarEstadoMeta(metaId, metaPayload, fallbackPerfilNome = '') {
        if (!metaId || !metaPayload) return;

        const existente = metasState.get(metaId) || { reservas: [] };

        const metaAtualizada = {
            id: metaId,
            nome: metaPayload.nome || existente.nome || 'Meta',
            valorAlvo: metaPayload.valor_alvo ?? existente.valorAlvo ?? 0,
            valorAtual: metaPayload.valor_atual ?? existente.valorAtual ?? 0,
            progressoPercentual: metaPayload.progresso_percentual ?? existente.progressoPercentual ?? 0,
            dataLimite: metaPayload.data_limite || existente.dataLimite || new Date().toISOString(),
            idPerfil: metaPayload.id_perfil ?? existente.idPerfil ?? null,
            perfilNome: fallbackPerfilNome || existente.perfilNome || '',
            estaConcluida: Boolean(metaPayload.esta_concluida ?? existente.estaConcluida),
            concluidaEm: metaPayload.concluida_em || existente.concluidaEm || null,
            reservas: existente.reservas || [],
        };

        metasState.set(metaId, metaAtualizada);
    }

    function registrarReservaNaMeta(metaId, reservaData) {
        const meta = metasState.get(metaId);
        if (!meta || !reservaData) return;

        const novaReserva = normalizarReserva(reservaData);
        const reservas = Array.isArray(meta.reservas) ? [...meta.reservas] : [];
        const index = reservas.findIndex(item => item.id === novaReserva.id);

        if (index >= 0) {
            reservas[index] = novaReserva;
        } else {
            reservas.push(novaReserva);
        }

        reservas.sort((a, b) => {
            const dataA = new Date(a.criado_em || a.atualizado_em || 0).getTime();
            const dataB = new Date(b.criado_em || b.atualizado_em || 0).getTime();
            return dataB - dataA;
        });

        metasState.set(metaId, { ...meta, reservas });
    }

    function removerReservaDaMeta(metaId, reservaId) {
        const meta = metasState.get(metaId);
        if (!meta) return;
        const reservasFiltradas = (meta.reservas || []).filter(item => item.id !== reservaId);
        metasState.set(metaId, { ...meta, reservas: reservasFiltradas });
    }

    async function carregarPerfis() {
        try {
            const perfis = await api.getPerfis();
            if (!perfilSelect) return;
            perfilSelect.innerHTML = '<option value="">Selecione um perfil</option>';
            perfis.forEach((perfil) => {
                const option = document.createElement('option');
                option.value = perfil.id;
                option.textContent = perfil.nome;
                perfilSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Não foi possível carregar perfis', error);
            showFeedback('Não foi possível carregar os perfis agora. Você pode continuar sem vincular um perfil.', 'warning');
        }
    }

    async function carregarMetas() {
        if (!metasContainer) return;
        try {
            const data = await api.getMetasDisponiveis();
            const metas = data?.metas || [];
            const idsAtivos = new Set();

            metas.forEach((meta) => {
                const metaId = meta.id;
                idsAtivos.add(metaId);
                const existente = metasState.get(metaId);
                metasState.set(metaId, {
                    id: metaId,
                    nome: meta.nome,
                    valorAlvo: meta.valor_alvo,
                    valorAtual: meta.valor_atual,
                    progressoPercentual: meta.progresso_percentual,
                    dataLimite: meta.data_limite,
                    idPerfil: existente?.idPerfil ?? null,
                    perfilNome: existente?.perfilNome || '',
                    estaConcluida: false,
                    concluidaEm: null,
                    reservas: existente?.reservas || [],
                });
            });

            Array.from(metasState.entries()).forEach(([id, meta]) => {
                if (!meta) return;
                if (!meta.estaConcluida && !idsAtivos.has(id)) {
                    metasState.delete(id);
                }
            });

            if (metasEmpty) {
                if (metas.length === 0) {
                    metasEmpty.classList.remove('hidden');
                    if (data?.mensagem) {
                        const titulo = metasEmpty.querySelector('strong');
                        if (titulo) titulo.textContent = data.mensagem;
                    }
                } else {
                    metasEmpty.classList.add('hidden');
                }
            }

            renderMetas();
        } catch (error) {
            console.error(error);
            showFeedback(error.message || 'Não foi possível carregar as metas.', 'error');
        }
    }

    function renderMetas() {
        if (!metasContainer) return;

        metasContainer.innerHTML = '';
        if (metasConcluidasContainer) {
            metasConcluidasContainer.innerHTML = '';
        }

        const metasAbertas = [];
        const metasFinalizadas = [];

        metasState.forEach((meta) => {
            if (meta.estaConcluida) {
                metasFinalizadas.push(meta);
            } else {
                metasAbertas.push(meta);
            }
        });

        metasAbertas.sort((a, b) => new Date(a.dataLimite).getTime() - new Date(b.dataLimite).getTime());
        metasFinalizadas.sort((a, b) => {
            const dataA = new Date(a.concluidaEm || a.dataLimite).getTime();
            const dataB = new Date(b.concluidaEm || b.dataLimite).getTime();
            return dataB - dataA;
        });

        if (metasAbertas.length === 0) {
            metasEmpty?.classList.remove('hidden');
        } else {
            metasEmpty?.classList.add('hidden');
            metasAbertas.forEach((meta) => {
                metasContainer.appendChild(buildMetaCard(meta, false));
            });
        }

        if (metasConcluidasCard) {
            if (metasFinalizadas.length === 0) {
                metasConcluidasCard.classList.add('hidden');
            } else {
                metasConcluidasCard.classList.remove('hidden');
                metasFinalizadas.forEach((meta) => {
                    metasConcluidasContainer.appendChild(buildMetaCard(meta, true));
                });
            }
        }
    }

    function buildMetaCard(meta, concluida) {
        const progresso = Math.min(100, Math.max(0, Math.round(meta.progressoPercentual || 0)));
        const perfilLabel = meta.perfilNome || 'Não vinculado';
        const deadlineLabel = concluida && meta.concluidaEm
            ? `Concluída em ${formatDateValue(meta.concluidaEm)}`
            : `Até ${formatDateValue(meta.dataLimite)}`;
        const card = document.createElement('article');
        card.className = concluida ? 'meta-card meta-card-concluida' : 'meta-card';
        card.dataset.metaId = meta.id;

        card.innerHTML = `
            <div class="meta-card-header">
                <div>
                    <h3>${meta.nome}</h3>
                    <p class="meta-perfil">Perfil vinculado: ${perfilLabel}</p>
                </div>
                <div style="text-align: right;">
                    <span class="meta-deadline">${deadlineLabel}</span>
                    ${concluida ? '<span class="meta-tag meta-tag-success">Concluída</span>' : ''}
                </div>
            </div>
            <div class="meta-progress-bar">
                <div class="meta-progress-fill" style="width: ${progresso}%;"></div>
            </div>
            <div class="meta-progress-values">
                <span>${formatCurrency(meta.valorAtual)} / ${formatCurrency(meta.valorAlvo)}</span>
                <span>${progresso}%</span>
            </div>
            <div class="meta-actions-row">
                <button type="button" class="btn-primary btn-small" data-action="abrir-reserva" data-meta-id="${meta.id}">Registrar reserva</button>
            </div>
            <p class="meta-reservas-title">Reservas registradas</p>
        `;

        const reservasList = document.createElement('ul');
        reservasList.className = 'meta-reservas-list';
        reservasList.dataset.metaId = meta.id;

        if (meta.reservas && meta.reservas.length) {
            meta.reservas.forEach((reserva) => {
                reservasList.appendChild(buildReservaItem(meta, reserva));
            });
        } else {
            const vazio = document.createElement('li');
            vazio.className = 'meta-reserva-item meta-reserva-empty';
            vazio.dataset.metaId = meta.id;
            vazio.textContent = 'Nenhuma reserva registrada nesta sessão.';
            reservasList.appendChild(vazio);
        }

        card.appendChild(reservasList);
        return card;
    }

    function buildReservaItem(meta, reserva) {
        const item = document.createElement('li');
        item.className = 'meta-reserva-item';
        item.dataset.metaId = meta.id;
        item.dataset.reservaId = reserva.id;

        const info = document.createElement('div');
        info.className = 'meta-reserva-info';

        const valorSpan = document.createElement('span');
        valorSpan.className = 'meta-reserva-valor';
        valorSpan.textContent = formatCurrency(reserva.valor);

        const dataSpan = document.createElement('span');
        dataSpan.textContent = formatDateTimeValue(reserva.criado_em || reserva.atualizado_em);

        info.append(valorSpan, dataSpan);
        item.appendChild(info);

        if (reserva.observacao) {
            const obs = document.createElement('p');
            obs.className = 'meta-reserva-obs';
            obs.textContent = reserva.observacao;
            item.appendChild(obs);
        }

        const actions = document.createElement('div');
        actions.className = 'meta-reserva-actions';

        const editButton = document.createElement('button');
        editButton.type = 'button';
        editButton.className = 'btn-inline';
        editButton.dataset.action = 'editar-reserva';
        editButton.dataset.metaId = meta.id;
        editButton.dataset.reservaId = reserva.id;
        editButton.textContent = 'Editar';

        const deleteButton = document.createElement('button');
        deleteButton.type = 'button';
        deleteButton.className = 'btn-inline btn-danger';
        deleteButton.dataset.action = 'excluir-reserva';
        deleteButton.dataset.metaId = meta.id;
        deleteButton.dataset.reservaId = reserva.id;
        deleteButton.textContent = 'Excluir';

        actions.append(editButton, deleteButton);
        item.appendChild(actions);

        return item;
    }

    function abrirModalReserva(metaId, modo, reservaId = null) {
        const meta = metasState.get(metaId);
        if (!meta || !modalReserva) {
            showFeedback('Meta não encontrada.', 'error');
            return;
        }

        reservaModalMode = modo;
        modalReserva.classList.remove('hidden');
        modalReservaTitulo.textContent = modo === 'create' ? 'Registrar reserva' : 'Editar reserva';
        modalReservaMeta.textContent = `${meta.nome} • Progresso ${formatCurrency(meta.valorAtual)} de ${formatCurrency(meta.valorAlvo)}`;

        inputReservaMetaId.value = metaId;
        inputReservaId.value = reservaId || '';
        inputReservaValor.value = '';
        inputReservaObservacao.value = '';

        if (modo === 'edit' && reservaId) {
            const reserva = (meta.reservas || []).find(item => item.id === reservaId);
            if (reserva) {
                inputReservaValor.value = reserva.valor;
                inputReservaObservacao.value = reserva.observacao || '';
            }
            btnSalvarReserva.textContent = 'Atualizar';
        } else {
            btnSalvarReserva.textContent = 'Salvar';
        }

        btnSalvarReserva.disabled = false;
        setTimeout(() => inputReservaValor.focus(), 0);
    }

    function fecharModalReserva() {
        if (!modalReserva) return;
        modalReserva.classList.add('hidden');
        formReserva?.reset();
        inputReservaMetaId.value = '';
        inputReservaId.value = '';
        btnSalvarReserva.textContent = 'Salvar';
        reservaModalMode = 'create';
    }

    function abrirModalExclusao(metaId, reservaId) {
        if (!modalConfirmReserva) return;
        const meta = metasState.get(metaId);
        const reserva = meta?.reservas?.find(item => item.id === reservaId);

        reservaParaExcluir = { metaId, reservaId };
        confirmText.textContent = reserva
            ? `Remover reserva de ${formatCurrency(reserva.valor)} da meta "${meta?.nome}"?`
            : 'Tem certeza que deseja remover esta reserva?';

        modalConfirmReserva.classList.remove('hidden');
    }

    function fecharModalExclusao() {
        if (!modalConfirmReserva) return;
        modalConfirmReserva.classList.add('hidden');
        reservaParaExcluir = null;
    }

    function adicionarMetaManual(metaCriada, perfilNome) {
        if (!metaCriada) return;
        metasState.set(metaCriada.id, {
            id: metaCriada.id,
            nome: metaCriada.nome,
            valorAlvo: metaCriada.valor_alvo,
            valorAtual: 0,
            progressoPercentual: 0,
            dataLimite: metaCriada.data_limite,
            idPerfil: perfilNome ? perfilSelect?.value || null : null,
            perfilNome,
            estaConcluida: false,
            concluidaEm: null,
            reservas: [],
        });
        renderMetas();
    }

    metasContainer?.addEventListener('click', (event) => {
        const action = event.target.dataset?.action;
        if (!action) return;
        const metaId = event.target.dataset.metaId;
        if (!metaId) return;

        if (action === 'abrir-reserva') {
            abrirModalReserva(metaId, 'create');
        } else if (action === 'editar-reserva') {
            const reservaId = event.target.dataset.reservaId;
            abrirModalReserva(metaId, 'edit', reservaId);
        } else if (action === 'excluir-reserva') {
            const reservaId = event.target.dataset.reservaId;
            abrirModalExclusao(metaId, reservaId);
        }
    });

    metasConcluidasContainer?.addEventListener('click', (event) => {
        const action = event.target.dataset?.action;
        if (!action) return;
        const metaId = event.target.dataset.metaId;
        if (!metaId) return;

        if (action === 'abrir-reserva') {
            abrirModalReserva(metaId, 'create');
        } else if (action === 'editar-reserva') {
            const reservaId = event.target.dataset.reservaId;
            abrirModalReserva(metaId, 'edit', reservaId);
        } else if (action === 'excluir-reserva') {
            const reservaId = event.target.dataset.reservaId;
            abrirModalExclusao(metaId, reservaId);
        }
    });

    btnCancelarReserva?.addEventListener('click', (event) => {
        event.preventDefault();
        fecharModalReserva();
    });

    modalReserva?.addEventListener('click', (event) => {
        if (event.target === modalReserva) {
            fecharModalReserva();
        }
    });

    btnCancelarReservaExclusao?.addEventListener('click', (event) => {
        event.preventDefault();
        fecharModalExclusao();
    });

    modalConfirmReserva?.addEventListener('click', (event) => {
        if (event.target === modalConfirmReserva) {
            fecharModalExclusao();
        }
    });

    btnConfirmarReservaExclusao?.addEventListener('click', async () => {
        if (!reservaParaExcluir) return;
        const { metaId, reservaId } = reservaParaExcluir;
        try {
            btnConfirmarReservaExclusao.disabled = true;
            const resposta = await api.excluirReserva(reservaId);
            removerReservaDaMeta(metaId, reservaId);
            const metaAtual = metasState.get(metaId);
            atualizarEstadoMeta(metaId, resposta.meta, metaAtual?.perfilNome || '');
            renderMetas();
            showFeedback(resposta.mensagem || 'Reserva removida com sucesso.', 'success');
        } catch (error) {
            console.error(error);
            showFeedback(error.message || 'Não foi possível remover a reserva.', 'error');
        } finally {
            btnConfirmarReservaExclusao.disabled = false;
            fecharModalExclusao();
        }
    });

    formReserva?.addEventListener('submit', async (event) => {
        event.preventDefault();

        const metaId = inputReservaMetaId.value;
        const valor = Number(inputReservaValor.value);
        const observacao = inputReservaObservacao.value.trim();

        if (!metaId) {
            showFeedback('Selecione uma meta válida.', 'error');
            return;
        }
        if (Number.isNaN(valor) || valor <= 0) {
            showFeedback('Informe um valor numérico maior que zero para a reserva.', 'error');
            return;
        }

        try {
            btnSalvarReserva.disabled = true;
            btnSalvarReserva.textContent = reservaModalMode === 'create' ? 'Salvando...' : 'Atualizando...';

            let resposta;
            if (reservaModalMode === 'create') {
                resposta = await api.criarReserva({
                    id_meta: metaId,
                    valor,
                    observacao: observacao || undefined,
                });
            } else {
                const reservaId = inputReservaId.value;
                resposta = await api.atualizarReserva(reservaId, {
                    valor,
                    observacao: observacao || null,
                });
            }

            const metaAtual = metasState.get(metaId);
            atualizarEstadoMeta(metaId, resposta.meta, metaAtual?.perfilNome || '');
            if (resposta.reserva) {
                registrarReservaNaMeta(metaId, resposta.reserva);
            }

            renderMetas();
            fecharModalReserva();

            const mensagem = resposta.mensagem
                || (reservaModalMode === 'create' ? 'Reserva registrada com sucesso.' : 'Reserva atualizada com sucesso.');
            showFeedback(mensagem, 'success');
        } catch (error) {
            console.error(error);
            showFeedback(error.message || 'Não foi possível salvar a reserva.', 'error');
        } finally {
            btnSalvarReserva.disabled = false;
            btnSalvarReserva.textContent = reservaModalMode === 'create' ? 'Salvar' : 'Atualizar';
        }
    });

    btnRecarregarMetas?.addEventListener('click', () => {
        carregarMetas();
    });

    btnIrCriarMeta?.addEventListener('click', () => {
        if (!form) return;
        const offsetTop = form.getBoundingClientRect().top + window.scrollY - 80;
        window.scrollTo({ top: offsetTop < 0 ? 0 : offsetTop, behavior: 'smooth' });
        nomeInput?.focus();
    });

    form?.addEventListener('submit', async (event) => {
        event.preventDefault();
        resetFeedback();

        const nome = nomeInput.value.trim();
        const dataValor = dataInput.value;
        const perfilId = perfilSelect.value;

        if (!nome) {
            showFeedback('Informe um nome para a meta.', 'error');
            return;
        }

        const valor = valorInput.valueAsNumber;
        if (Number.isNaN(valor) || valor <= 0) {
            showFeedback('Informe um valor numérico maior que zero.', 'error');
            return;
        }

        if (!dataValor) {
            showFeedback('Selecione uma data limite para planejar a meta.', 'error');
            return;
        }

        const dataSelecionada = new Date(`${dataValor}T00:00:00`);
        const hojeComparacao = new Date();
        hojeComparacao.setHours(0, 0, 0, 0);
        if (dataSelecionada <= hojeComparacao) {
            showFeedback('A data limite deve ser futura.', 'error');
            return;
        }

        const payload = {
            nome,
            valor,
            data_limite: dataValor,
        };
        if (perfilId) {
            payload.id_perfil = perfilId;
        }

        const perfilNome = perfilId ? perfilSelect.options[perfilSelect.selectedIndex]?.textContent : 'Não vinculado';

        try {
            btnSubmit.disabled = true;
            btnSubmit.textContent = 'Criando...';

            const metaCriada = await api.criarMeta(payload);

            showFeedback('Meta criada com sucesso! Confira o plano sugerido abaixo.', 'success');
            preencherSugestoes(metaCriada, perfilNome);
            adicionarMetaManual(metaCriada, perfilNome);
            await carregarMetas();

            const metaAtualizada = metasState.get(metaCriada.id);
            if (metaAtualizada && !metaAtualizada.perfilNome) {
                metaAtualizada.perfilNome = perfilNome;
                metasState.set(metaCriada.id, metaAtualizada);
                renderMetas();
            }

            form.reset();
            if (dataInput) dataInput.value = dataInput.min;
        } catch (error) {
            console.error(error);
            showFeedback(error.message || 'Não foi possível criar a meta.', 'error');
        } finally {
            btnSubmit.disabled = false;
            btnSubmit.textContent = 'Criar meta';
        }
    });

    function preencherSugestoes(meta, perfilNome) {
        if (!meta) return;
        resumoNome.textContent = meta.nome;
        resumoValor.textContent = formatCurrency(meta.valor_alvo);
        resumoData.textContent = formatDateValue(meta.data_limite);
        resumoPerfil.textContent = perfilNome || 'Não vinculado';
        if (meta.sugestoes) {
            reservaSemanal.textContent = formatCurrency(meta.sugestoes.semanal);
            reservaMensal.textContent = formatCurrency(meta.sugestoes.mensal);
        }
        sugestoesCard?.classList.remove('hidden');
    }

    carregarPerfis();
    carregarMetas();
});
