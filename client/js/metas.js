import { api, API_URL } from "./api.js";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-criar-meta");
  const feedbackEl = document.getElementById("meta-feedback");
  const sugestoesCard = document.getElementById("meta-sugestoes-card");
  const btnSubmit = document.getElementById("btn-criar-meta");

  const nomeInput = document.getElementById("meta-nome");
  const valorInput = document.getElementById("meta-valor");
  const dataInput = document.getElementById("meta-data");
  const perfilSelect = document.getElementById("meta-perfil");

  const resumoNome = document.getElementById("resumo-nome");
  const resumoValor = document.getElementById("resumo-valor");
  const resumoData = document.getElementById("resumo-data");
  const resumoPerfil = document.getElementById("resumo-perfil");
  const reservaSemanal = document.getElementById("reserva-semanal");
  const reservaMensal = document.getElementById("reserva-mensal");

  const metasContainer = document.getElementById("metas-list");
  const metasEmpty = document.getElementById("metas-empty");
  const btnRecarregarMetas = document.getElementById("btn-recarregar-metas");
  const btnIrCriarMeta = document.getElementById("btn-ir-criar-meta");
  const metasConcluidasCard = document.getElementById("metas-concluidas-card");
  const metasConcluidasContainer = document.getElementById("metas-concluidas");
  const metasArquivadasCard = document.getElementById("metas-arquivadas-card");
  const metasArquivadasContainer = document.getElementById("metas-arquivadas");

  const modalReserva = document.getElementById("modal-reserva");
  const modalReservaTitulo = document.getElementById("modal-reserva-titulo");
  const modalReservaMeta = document.getElementById("modal-reserva-meta");
  const formReserva = document.getElementById("form-reserva");
  const inputReservaMetaId = document.getElementById("reserva-meta-id");
  const inputReservaId = document.getElementById("reserva-id");
  const inputReservaValor = document.getElementById("reserva-valor");
  const inputReservaObservacao = document.getElementById("reserva-observacao");
  const btnCancelarReserva = document.getElementById("btn-cancelar-reserva");
  const btnSalvarReserva = document.getElementById("btn-salvar-reserva");

  const modalConfirmReserva = document.getElementById("modal-confirm-reserva");
  const confirmText = document.getElementById("confirm-reserva-text");
  const btnCancelarReservaExclusao = document.getElementById(
    "btn-cancelar-reserva-exclusao"
  );
  const btnConfirmarReservaExclusao = document.getElementById(
    "btn-confirmar-reserva-exclusao"
  );

  const modalDetalhesMeta = document.getElementById("modal-detalhes-meta");
  const detalhesMetaNome = document.getElementById("detalhes-meta-nome");
  const detalhesMetaStatus = document.getElementById("detalhes-meta-status");
  const detalhesMetaEconomizado = document.getElementById(
    "detalhes-meta-economizado"
  );
  const detalhesMetaUtilizado = document.getElementById(
    "detalhes-meta-utilizado"
  );
  const detalhesMetaSaldo = document.getElementById("detalhes-meta-saldo");
  const detalhesMetaDiferenca = document.getElementById(
    "detalhes-meta-diferenca"
  );
  const detalhesMetaObservacao = document.getElementById(
    "detalhes-meta-observacao"
  );
  const btnFecharDetalhesMeta = document.getElementById(
    "btn-fechar-detalhes-meta"
  );
  const btnRegistrarUsoMeta = document.getElementById(
    "btn-registrar-uso-meta"
  );
  const btnLiberarSaldoMeta = document.getElementById("btn-liberar-saldo-meta");

  const modalRegistrarUso = document.getElementById("modal-registrar-uso");
  const formRegistrarUso = document.getElementById("form-registrar-uso");
  const registrarUsoResumo = document.getElementById("registrar-uso-resumo");
  const registrarUsoSelect = document.getElementById("registrar-uso-transacao");
  const registrarUsoSemTransacoes = document.getElementById(
    "registrar-uso-sem-transacoes"
  );
  const registrarUsoEconomizado = document.getElementById(
    "registrar-uso-economizado"
  );
  const registrarUsoUtilizado = document.getElementById(
    "registrar-uso-utilizado"
  );
  const registrarUsoSaldo = document.getElementById("registrar-uso-saldo");
  const registrarUsoDiferenca = document.getElementById(
    "registrar-uso-diferenca"
  );
  const registrarUsoPanel = document.getElementById("registrar-uso-panel");
  const btnCancelarRegistrarUso = document.getElementById(
    "btn-cancelar-registrar-uso"
  );
  const btnConfirmarRegistrarUso = document.getElementById(
    "btn-confirmar-registrar-uso"
  );

  const modalEditarMeta = document.getElementById("modal-editar-meta");
  const formEditarMeta = document.getElementById("form-editar-meta");
  const editarMetaIdInput = document.getElementById("editar-meta-id");
  const editarMetaNomeInput = document.getElementById("editar-meta-nome");
  const editarMetaValorInput = document.getElementById("editar-meta-valor");
  const editarMetaDataInput = document.getElementById("editar-meta-data");
  const editarMetaProgresso = document.getElementById("editar-meta-progresso");
  const btnCancelarEdicaoMeta = document.getElementById(
    "btn-cancelar-edicao-meta"
  );
  const btnSalvarEdicaoMeta = document.getElementById("btn-salvar-edicao-meta");

  const modalConfirmMeta = document.getElementById("modal-confirm-meta");
  const confirmMetaTitle = document.getElementById("confirm-meta-title");
  const confirmMetaMessage = document.getElementById("confirm-meta-message");
  const btnCancelarConfirmMeta = document.getElementById(
    "btn-cancelar-confirm-meta"
  );
  const btnConfirmMeta = document.getElementById("btn-confirm-meta");

  const modalCancelarMeta = document.getElementById("modal-cancelar-meta");
  const formCancelarMeta = document.getElementById("form-cancelar-meta");
  const cancelarMetaResumo = document.getElementById("cancelar-meta-resumo");
  const cancelarMetaDestinoGroup = document.getElementById(
    "cancelar-meta-destino-group"
  );
  const cancelarMetaDestinoSelect = document.getElementById(
    "cancelar-meta-destino"
  );
  const cancelarMetaSemOpcoes = document.getElementById(
    "cancelar-meta-sem-opcoes"
  );
  const btnCancelarCancelamentoMeta = document.getElementById(
    "btn-cancelar-cancelamento-meta"
  );
  const btnConfirmarCancelamentoMeta = document.getElementById(
    "btn-confirmar-cancelamento-meta"
  );

  const confettiContainer = document.getElementById("confetti-container");

  const metasState = new Map();
  const metaDetalhesCache = new Map();
  let reservaModalMode = "create";
  let reservaParaExcluir = null;
  let metaEmEdicao = null;
  let confirmMetaCallback = null;
  let metaParaCancelar = null;
  let metaEmDetalhe = null;
  let metaParaRegistrarUso = null;
  let transacoesCache = null;
  let confettiTimeout = null;
  let detalhesMetaAtual = null;

  const currencyFormatter = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
  const dateFormatter = new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "medium",
  });
  const dateTimeFormatter = new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  });

  const minDate = new Date();
  minDate.setDate(minDate.getDate() + 1);
  minDate.setMinutes(minDate.getMinutes() - minDate.getTimezoneOffset());
  if (dataInput) {
    dataInput.min = minDate.toISOString().split("T")[0];
    dataInput.value = dataInput.min;
  }

  function resetFeedback() {
    if (!feedbackEl) return;
    feedbackEl.className = "hidden";
    feedbackEl.textContent = "";
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
    if (!value) return "-";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "-";
    return dateFormatter.format(date);
  }

  function formatDateTimeValue(value) {
    if (!value) return "Data indisponível";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "Data indisponível";
    return dateTimeFormatter.format(date);
  }

  function calcularProgresso(valorAtual, valorAlvo) {
    if (!valorAlvo || Number(valorAlvo) === 0) {
      return 0;
    }
    return Math.min(
      100,
      Math.max(0, Math.round((Number(valorAtual) / Number(valorAlvo)) * 100))
    );
  }

  function normalizarReserva(reserva) {
    return {
      id: reserva.id,
      id_meta: reserva.id_meta,
      valor: Number(reserva.valor),
      observacao: reserva.observacao || "",
      criado_em: reserva.criado_em || null,
      atualizado_em: reserva.atualizado_em || null,
    };
  }

  function atualizarEstadoMeta(metaId, metaPayload, fallbackPerfilNome = "") {
    if (!metaId || !metaPayload) return null;

    const jaExistia = metasState.has(metaId);
    const existente = metasState.get(metaId) || { reservas: [] };
    const statusAnterior = (existente.status || "ATIVA").toString().toUpperCase();
    const valorAtualBruto =
      metaPayload.valor_atual ?? existente.valorAtual ?? existente.valor_atual ?? 0;
    const valorAlvoBruto =
      metaPayload.valor_alvo ?? existente.valorAlvo ?? existente.valor_alvo ?? 0;
    const valorAtual = Number(valorAtualBruto) || 0;
    const valorAlvo = Number(valorAlvoBruto) || 0;
    const statusNormalizado = (metaPayload.status || existente.status || "ATIVA")
      .toString()
      .toUpperCase();
    const progressoPercentual =
      metaPayload.progresso_percentual ??
      existente.progressoPercentual ??
      calcularProgresso(valorAtual, valorAlvo);
    const finalizadaEm =
      metaPayload.finalizada_em || existente.finalizadaEm || null;
    const finalizadaFlag = Boolean(
      metaPayload.finalizada ?? existente.finalizada ?? (finalizadaEm !== null)
    );
    const valorUtilizado = Math.abs(
      Number(
        metaPayload.valor_utilizado ??
          existente.valorUtilizado ??
          existente.valor_utilizado ??
          0
      ) || 0
    );
    const saldoRestante = Math.max(0, valorAtual - valorUtilizado);
    const acabouDeConcluir =
      jaExistia && statusNormalizado === "CONCLUIDA" && statusAnterior !== "CONCLUIDA";

    const metaAtualizada = {
      id: metaId,
      nome: metaPayload.nome || existente.nome || "Meta",
      valorAlvo,
      valorAtual,
      progressoPercentual,
      dataLimite:
        metaPayload.data_limite ||
        existente.dataLimite ||
        new Date().toISOString(),
      idPerfil: metaPayload.id_perfil ?? existente.idPerfil ?? null,
      perfilNome: fallbackPerfilNome || existente.perfilNome || "",
      estaConcluida: Boolean(
        metaPayload.esta_concluida ?? existente.estaConcluida
      ),
      concluidaEm: metaPayload.concluida_em || existente.concluidaEm || null,
      status: statusNormalizado,
      reservas: existente.reservas || [],
      finalizadaEm,
      finalizada: finalizadaFlag,
      valorUtilizado,
      saldoRestante,
      foiConcluidaAgora: acabouDeConcluir,
    };

    metasState.set(metaId, metaAtualizada);
    return metaAtualizada;
  }

  function registrarReservaNaMeta(metaId, reservaData) {
    const meta = metasState.get(metaId);
    if (!meta || !reservaData) return;

    const novaReserva = normalizarReserva(reservaData);
    const reservas = Array.isArray(meta.reservas) ? [...meta.reservas] : [];
    const index = reservas.findIndex((item) => item.id === novaReserva.id);

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
    const reservasFiltradas = (meta.reservas || []).filter(
      (item) => item.id !== reservaId
    );
    metasState.set(metaId, { ...meta, reservas: reservasFiltradas });
  }

  function dispararConfete() {
    if (!confettiContainer) return;

    if (confettiTimeout) {
      clearTimeout(confettiTimeout);
      confettiTimeout = null;
    }

    confettiContainer.innerHTML = "";
    confettiContainer.classList.remove("hidden");

    const cores = ["#3b82f6", "#f97316", "#22c55e", "#a855f7", "#eab308"];
    const quantidade = 32;

    for (let i = 0; i < quantidade; i += 1) {
      const piece = document.createElement("span");
      piece.className = "confetti-piece";
      piece.style.left = `${Math.random() * 100}%`;
      piece.style.backgroundColor = cores[i % cores.length];
      piece.style.animationDelay = `${Math.random() * 0.3}s`;
      piece.style.transform = `rotate(${Math.random() * 360}deg)`;
      confettiContainer.appendChild(piece);
    }

    confettiTimeout = setTimeout(() => {
      confettiContainer.classList.add("hidden");
      confettiContainer.innerHTML = "";
      confettiTimeout = null;
    }, 1900);
  }

  function celebrarConclusao(meta) {
    if (!meta) return;
    dispararConfete();
    showFeedback(
      `Meta "${meta.nome}" concluída! Parabéns pelo objetivo alcançado!`,
      "success"
    );
  }

  async function carregarDetalhesMeta(metaId, useCache = true) {
    if (!metaId) return null;
    if (!useCache) {
      metaDetalhesCache.delete(metaId);
    }
    if (useCache && metaDetalhesCache.has(metaId)) {
      const cached = metaDetalhesCache.get(metaId);
      atualizarEstadoMeta(metaId, {
        valor_alvo: cached.valor_alvo,
        valor_atual: cached.valor_economizado,
        status: cached.status,
        concluida_em: cached.concluida_em,
        finalizada_em: cached.finalizada_em,
        esta_concluida: cached.concluida,
        finalizada: cached.finalizada,
        valor_utilizado: cached.valor_utilizado,
        saldo_restante: cached.saldo_restante,
      });
      return cached;
    }

    const detalhes = await api.obterDetalhesMeta(metaId);
    metaDetalhesCache.set(metaId, detalhes);
    atualizarEstadoMeta(metaId, {
      nome: detalhes.nome,
      valor_alvo: detalhes.valor_alvo,
      valor_atual: detalhes.valor_economizado,
      status: detalhes.status,
      concluida_em: detalhes.concluida_em,
      finalizada_em: detalhes.finalizada_em,
      esta_concluida: detalhes.concluida,
      finalizada: detalhes.finalizada,
      valor_utilizado: detalhes.valor_utilizado,
      saldo_restante: detalhes.saldo_restante,
    });
    return detalhes;
  }

  function calcularDiferenca(economizado, utilizado) {
    return Number(economizado || 0) - Number(utilizado || 0);
  }

  function aplicarClasseDiferenca(elemento, diferenca) {
    if (!elemento) return;
    elemento.classList.remove("meta-negative", "meta-positive");
    if (diferenca < 0) {
      elemento.classList.add("meta-negative");
    } else if (diferenca > 0) {
      elemento.classList.add("meta-positive");
    }
  }

  function preencherDetalhesMetaView(meta, detalhes) {
    if (!meta || !detalhes) return;

    detalhesMetaNome.textContent = meta.nome;

    const statusMensagem = detalhes.finalizada
      ? `Finalizada${detalhes.finalizada_em ? ` em ${formatDateValue(detalhes.finalizada_em)}` : ""}`
      : `Concluída${detalhes.concluida_em ? ` em ${formatDateValue(detalhes.concluida_em)}` : ""}`;
    detalhesMetaStatus.textContent = statusMensagem;

    const economizadoValor = Number(detalhes.valor_economizado || 0);
    const utilizadoValor = Math.abs(Number(detalhes.valor_utilizado || 0));
    const saldoCalculado = Math.max(0, economizadoValor - utilizadoValor);

    detalhesMetaEconomizado.textContent = formatCurrency(economizadoValor);
    detalhesMetaUtilizado.textContent = formatCurrency(utilizadoValor);
    detalhesMetaSaldo.textContent = formatCurrency(saldoCalculado);
    const diferenca = calcularDiferenca(economizadoValor, utilizadoValor);
    detalhesMetaDiferenca.textContent = formatCurrency(diferenca);
    aplicarClasseDiferenca(detalhesMetaDiferenca, diferenca);

    if (detalhes.finalizada) {
      detalhesMetaObservacao.textContent =
        "Meta finalizada. O histórico ficará disponível nas metas arquivadas.";
    } else {
      detalhesMetaObservacao.textContent =
        "Você pode registrar o uso do valor para vincular despesas ou liberar o saldo restante.";
    }

    if (detalhes.finalizada) {
      btnRegistrarUsoMeta?.classList.add("hidden");
      btnLiberarSaldoMeta?.classList.add("hidden");
    } else {
      btnRegistrarUsoMeta?.classList.remove("hidden");
      btnLiberarSaldoMeta?.classList.remove("hidden");
      btnLiberarSaldoMeta.disabled = saldoCalculado <= 0;
    }
  }

  function preencherPainelUso(detalhes, transacao = null) {
    if (!detalhes) return;
    const economizado = Number(detalhes.valor_economizado || 0);
    const utilizadoAtual = Math.abs(Number(detalhes.valor_utilizado || 0));
    const valorTransacao = transacao ? Math.abs(Number(transacao.valor || 0)) : 0;
    const utilizadoPrevisto = utilizadoAtual + valorTransacao;
    const saldoPrevisto = economizado - utilizadoPrevisto;
    const diferenca = calcularDiferenca(economizado, utilizadoPrevisto);

    registrarUsoEconomizado.textContent = formatCurrency(economizado);
    registrarUsoUtilizado.textContent = formatCurrency(utilizadoPrevisto);
    registrarUsoSaldo.textContent = formatCurrency(saldoPrevisto);
    registrarUsoDiferenca.textContent = formatCurrency(diferenca);
    aplicarClasseDiferenca(registrarUsoDiferenca, diferenca);
  }

  async function carregarTransacoes(force = false) {
    if (!force && Array.isArray(transacoesCache)) {
      return transacoesCache;
    }
    const transacoes = await api.getTransacoes();
    transacoesCache = Array.isArray(transacoes)
      ? transacoes.map((transacao) => ({
          ...transacao,
          valor: Math.abs(Number(transacao.valor || 0)),
        }))
      : [];
    return transacoesCache;
  }

  function preencherSelectTransacoes(transacoes) {
    if (!registrarUsoSelect) return [];
    registrarUsoSelect.innerHTML = "";

    const despesas = (transacoes || []).filter(
      (item) => (item.tipo || "").toUpperCase() === "DESPESA"
    );

    if (despesas.length === 0) {
      registrarUsoSelect.disabled = true;
      registrarUsoSemTransacoes?.classList.remove("hidden");
      btnConfirmarRegistrarUso.disabled = true;
      return [];
    }

    registrarUsoSemTransacoes?.classList.add("hidden");
    registrarUsoSelect.disabled = false;

    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "Selecione uma despesa";
    registrarUsoSelect.appendChild(defaultOption);

    despesas
      .sort(
        (a, b) => new Date(b.data).getTime() - new Date(a.data).getTime()
      )
      .forEach((transacao) => {
        const option = document.createElement("option");
        option.value = transacao.id;
        option.dataset.valor = transacao.valor;
        option.dataset.descricao = transacao.descricao || "Despesa";
        option.textContent = `${transacao.descricao || "Despesa"} • ${formatCurrency(
          Math.abs(transacao.valor)
        )} • ${formatDateValue(transacao.data)}`;
        registrarUsoSelect.appendChild(option);
      });

    btnConfirmarRegistrarUso.disabled = true;
    return despesas;
  }

  async function abrirDetalhesMeta(meta) {
    if (!meta || !modalDetalhesMeta) return;
    try {
      const detalhes = await carregarDetalhesMeta(meta.id, false);
      detalhesMetaAtual = detalhes;
      metaEmDetalhe = metasState.get(meta.id) || meta;
      preencherDetalhesMetaView(metaEmDetalhe, detalhes);
      modalDetalhesMeta.classList.remove("hidden");
    } catch (error) {
      console.error(error);
      showFeedback(
        error.message || "Não foi possível carregar os detalhes da meta.",
        "error"
      );
    }
  }

  function fecharModalDetalhesMeta() {
    if (!modalDetalhesMeta) return;
    modalDetalhesMeta.classList.add("hidden");
    metaEmDetalhe = null;
    detalhesMetaAtual = null;
  }

  async function abrirModalRegistrarUso(meta) {
    if (!meta || !modalRegistrarUso) return;
    try {
      const detalhes = await carregarDetalhesMeta(meta.id, false);
      detalhesMetaAtual = detalhes;
      metaParaRegistrarUso = metasState.get(meta.id) || meta;

      registrarUsoResumo.textContent = `Meta "${meta.nome}" • ${formatCurrency(
        detalhes.valor_economizado
      )} economizados`;

      const transacoes = await carregarTransacoes();
      const despesas = preencherSelectTransacoes(transacoes);
      preencherPainelUso(detalhes);

      if (despesas.length === 0) {
        btnConfirmarRegistrarUso.disabled = true;
      }

      modalRegistrarUso.classList.remove("hidden");
    } catch (error) {
      console.error(error);
      showFeedback(
        error.message || "Não foi possível carregar as transações.",
        "error"
      );
    }
  }

  function fecharModalRegistrarUso() {
    if (!modalRegistrarUso) return;
    modalRegistrarUso.classList.add("hidden");
    formRegistrarUso?.reset();
    metaParaRegistrarUso = null;
    detalhesMetaAtual = null;
    registrarUsoSemTransacoes?.classList.add("hidden");
    btnConfirmarRegistrarUso.disabled = true;
    btnConfirmarRegistrarUso.textContent = "Registrar uso";
  }

  function abrirModalEditar(meta) {
    if (!modalEditarMeta || !formEditarMeta) return;
    metaEmEdicao = meta;
    editarMetaIdInput.value = meta.id;
    editarMetaNomeInput.value = meta.nome;
    editarMetaValorInput.value = Number(meta.valorAlvo || 0).toFixed(2);
    const dataLimiteIso = meta.dataLimite
      ? new Date(meta.dataLimite).toISOString().split("T")[0]
      : "";
    const minDate = new Date();
    minDate.setHours(0, 0, 0, 0);
    minDate.setDate(minDate.getDate() + 1);
    editarMetaDataInput.min = minDate.toISOString().split("T")[0];
    editarMetaDataInput.value = dataLimiteIso;

    const progressoAtual = calcularProgresso(meta.valorAtual, meta.valorAlvo);
    editarMetaProgresso.textContent = `Progresso atual: ${formatCurrency(
      meta.valorAtual
    )} (${progressoAtual}%)`;

    btnSalvarEdicaoMeta.disabled = false;
    btnSalvarEdicaoMeta.textContent = "Salvar alterações";

    modalEditarMeta.classList.remove("hidden");
    setTimeout(() => editarMetaNomeInput.focus(), 0);
  }

  function fecharModalEditar() {
    if (!modalEditarMeta) return;
    modalEditarMeta.classList.add("hidden");
    formEditarMeta?.reset();
    metaEmEdicao = null;
  }

  function setConfirmButtonVariant(variant = "primary") {
    if (!btnConfirmMeta) return;
    const variants = ["btn-primary", "btn-warning", "btn-danger", "btn-success"];
    btnConfirmMeta.classList.remove(...variants);
    switch (variant) {
      case "warning":
        btnConfirmMeta.classList.add("btn-warning");
        break;
      case "danger":
        btnConfirmMeta.classList.add("btn-danger");
        break;
      case "success":
        btnConfirmMeta.classList.add("btn-success");
        break;
      default:
        btnConfirmMeta.classList.add("btn-primary");
        break;
    }
  }

  function abrirModalConfirmacao({
    title,
    message,
    confirmLabel = "Confirmar",
    variant = "primary",
    onConfirm,
  }) {
    if (!modalConfirmMeta) return;
    confirmMetaTitle.textContent = title;
    confirmMetaMessage.textContent = message;
    btnConfirmMeta.textContent = confirmLabel;
    setConfirmButtonVariant(variant);
    confirmMetaCallback = onConfirm;
    btnConfirmMeta.disabled = false;
    modalConfirmMeta.classList.remove("hidden");
  }

  function fecharModalConfirmacao() {
    if (!modalConfirmMeta) return;
    modalConfirmMeta.classList.add("hidden");
    confirmMetaCallback = null;
    btnConfirmMeta.textContent = "Confirmar";
    setConfirmButtonVariant("primary");
  }

  function atualizarVisibilidadeRealocacao(acao) {
    if (!cancelarMetaDestinoGroup || !cancelarMetaDestinoSelect) return;
    if (acao === "realocar") {
      cancelarMetaDestinoGroup.classList.remove("hidden");
      if (!cancelarMetaDestinoSelect.disabled) {
        cancelarMetaDestinoSelect.focus();
      }
    } else {
      cancelarMetaDestinoGroup.classList.add("hidden");
      cancelarMetaDestinoSelect.value = "";
    }
  }

  function preencherMetasDestino(metaAtual) {
    if (!cancelarMetaDestinoSelect) return;
    cancelarMetaDestinoSelect.innerHTML = "";
    const metasDisponiveis = Array.from(metasState.values()).filter(
      (meta) => meta.id !== metaAtual.id && meta.status === "ATIVA"
    );

    cancelarMetaDestinoSelect.disabled = false;

    if (metasDisponiveis.length === 0) {
      cancelarMetaDestinoSelect.innerHTML = "";
      const option = document.createElement("option");
      option.value = "";
      option.textContent = "Nenhuma meta ativa disponível";
      cancelarMetaDestinoSelect.appendChild(option);
      cancelarMetaDestinoSelect.disabled = true;
      cancelarMetaSemOpcoes?.classList.remove("hidden");
      return;
    }

    cancelarMetaSemOpcoes?.classList.add("hidden");

    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "Selecione uma meta";
    cancelarMetaDestinoSelect.appendChild(defaultOption);

    metasDisponiveis.forEach((meta) => {
      const option = document.createElement("option");
      option.value = meta.id;
      option.textContent = `${meta.nome} • ${formatCurrency(meta.valorAtual)} / ${formatCurrency(
        meta.valorAlvo
      )}`;
      cancelarMetaDestinoSelect.appendChild(option);
    });
  }

  function abrirModalCancelar(meta) {
    if (!modalCancelarMeta || !formCancelarMeta) return;
    metaParaCancelar = meta;
    formCancelarMeta.reset();
    cancelarMetaResumo.textContent = `Meta "${meta.nome}" possui ${formatCurrency(
      meta.valorAtual
    )} reservados. Escolha o destino dos fundos.`;
    preencherMetasDestino(meta);

    const acaoAtual = formCancelarMeta.querySelector(
      'input[name="cancelar-acao"]:checked'
    )?.value;
    atualizarVisibilidadeRealocacao(acaoAtual || "manter");

    btnConfirmarCancelamentoMeta.disabled = false;
    btnConfirmarCancelamentoMeta.textContent = "Cancelar meta";

    modalCancelarMeta.classList.remove("hidden");
  }

  function fecharModalCancelar() {
    if (!modalCancelarMeta) return;
    modalCancelarMeta.classList.add("hidden");
    formCancelarMeta?.reset();
    cancelarMetaDestinoGroup?.classList.add("hidden");
    if (cancelarMetaDestinoSelect) {
      cancelarMetaDestinoSelect.value = "";
      cancelarMetaDestinoSelect.disabled = false;
    }
    cancelarMetaSemOpcoes?.classList.add("hidden");
    metaParaCancelar = null;
  }

  async function carregarPerfis() {
    try {
      const perfis = await api.getPerfis();
      if (!perfilSelect) return;
      perfilSelect.innerHTML = '<option value="">Selecione um perfil</option>';
      perfis.forEach((perfil) => {
        const option = document.createElement("option");
        option.value = perfil.id;
        option.textContent = perfil.nome;
        perfilSelect.appendChild(option);
      });
    } catch (error) {
      console.error("Não foi possível carregar perfis", error);
      showFeedback(
        "Não foi possível carregar os perfis agora. Você pode continuar sem vincular um perfil.",
        "warning"
      );
    }
  }

  async function carregarMetas() {
    if (!metasContainer) return;
    try {
      const response = await fetch(`${API_URL}/data/metas`);
      if (!response.ok) throw new Error("Não foi possível carregar as metas.");

      const metas = await response.json();
      const idsAtivos = new Set();

      metas.forEach((meta) => {
        const metaId = meta.id;
        idsAtivos.add(metaId);
        const existente = metasState.get(metaId);
        const metaAtualizada = atualizarEstadoMeta(
          metaId,
          {
            nome: meta.nome,
            valor_alvo: meta.valor_alvo,
            valor_atual: meta.valor_atual,
            data_limite: meta.data_limite,
            id_perfil: meta.id_perfil,
            status: meta.status,
            concluida_em: meta.concluida_em,
            esta_concluida: meta.status === "CONCLUIDA",
            finalizada_em: meta.finalizada_em,
            finalizada: Boolean(meta.finalizada_em),
          },
          existente?.perfilNome || ""
        );
        if (metaAtualizada) {
          metaAtualizada.foiConcluidaAgora = Boolean(
            metaAtualizada.foiConcluidaAgora && !metaAtualizada.finalizada
          );
          if (metaAtualizada.foiConcluidaAgora) {
            celebrarConclusao(metaAtualizada);
            metaAtualizada.foiConcluidaAgora = false;
            metasState.set(metaId, metaAtualizada);
          }
        }
      });

      Array.from(metasState.entries()).forEach(([id, meta]) => {
        if (!meta) return;
        if (!idsAtivos.has(id)) {
          metasState.delete(id);
        }
      });

      renderMetas();
    } catch (error) {
      console.error(error);
      showFeedback(
        error.message || "Não foi possível carregar as metas.",
        "error"
      );
    }
  }

  function renderMetas() {
    if (!metasContainer) return;

    metasContainer.innerHTML = "";
    if (metasConcluidasContainer) {
      metasConcluidasContainer.innerHTML = "";
    }
    if (metasArquivadasContainer) {
      metasArquivadasContainer.innerHTML = "";
    }

    const metasEmAndamento = [];
    const metasFinalizadas = [];
    const metasArquivadas = [];

    metasState.forEach((meta) => {
      if (!meta) return;
      const finalizada = Boolean(meta.finalizada || meta.finalizadaEm);
      if (meta.status === "CANCELADA" || finalizada) {
        metasArquivadas.push(meta);
      } else if (meta.status === "CONCLUIDA" || meta.estaConcluida) {
        metasFinalizadas.push(meta);
      } else {
        metasEmAndamento.push(meta);
      }
    });

    metasEmAndamento.sort(
      (a, b) =>
        new Date(a.dataLimite).getTime() - new Date(b.dataLimite).getTime()
    );
    metasFinalizadas.sort((a, b) => {
      const dataA = new Date(a.concluidaEm || a.dataLimite).getTime();
      const dataB = new Date(b.concluidaEm || b.dataLimite).getTime();
      return dataB - dataA;
    });
    metasArquivadas.sort((a, b) => {
      const dataA = new Date(a.dataLimite).getTime();
      const dataB = new Date(b.dataLimite).getTime();
      return dataB - dataA;
    });

    if (metasEmAndamento.length === 0) {
      metasEmpty?.classList.remove("hidden");
    } else {
      metasEmpty?.classList.add("hidden");
      metasEmAndamento.forEach((meta) => {
        metasContainer.appendChild(buildMetaCard(meta, false, false));
      });
    }

    if (metasConcluidasCard) {
      if (metasFinalizadas.length === 0) {
        metasConcluidasCard.classList.add("hidden");
      } else {
        metasConcluidasCard.classList.remove("hidden");
        metasFinalizadas.forEach((meta) => {
          metasConcluidasContainer.appendChild(
            buildMetaCard(meta, true, false)
          );
        });
      }
    }

    if (metasArquivadasCard) {
      if (metasArquivadas.length === 0) {
        metasArquivadasCard.classList.add("hidden");
      } else {
        metasArquivadasCard.classList.remove("hidden");
        metasArquivadas.forEach((meta) => {
          const concluida = meta.status === "CONCLUIDA" || meta.estaConcluida;
          metasArquivadasContainer.appendChild(
            buildMetaCard(meta, concluida, true)
          );
        });
      }
    }
  }

  function buildMetaCard(meta, concluida, arquivada = false) {
    const progresso = Math.min(
      100,
      Math.max(0, Math.round(meta.progressoPercentual || 0))
    );
    const perfilLabel = meta.perfilNome || "Não vinculado";
    let deadlineLabel = `Até ${formatDateValue(meta.dataLimite)}`;
    if (meta.finalizadaEm) {
      deadlineLabel = `Finalizada em ${formatDateValue(meta.finalizadaEm)}`;
    } else if (concluida && meta.concluidaEm) {
      deadlineLabel = `Concluída em ${formatDateValue(meta.concluidaEm)}`;
    }
    
    const card = document.createElement("article");
    if (concluida) {
      card.className = "meta-card meta-card-concluida";
    } else if (arquivada) {
      card.className = "meta-card meta-card-arquivada";
    } else {
      card.className = "meta-card";
    }
    card.dataset.metaId = meta.id;

    const statusTexto = meta.finalizada ? "FINALIZADA" : meta.status;
    const statusClass = (meta.finalizada ? "FINALIZADA" : meta.status || "ATIVA")
      .toString()
      .toLowerCase();

    card.innerHTML = `
            <div class="meta-card-header">
                <div>
                    <h3>${meta.nome}</h3>
                    <p class="meta-perfil">Perfil vinculado: ${perfilLabel}</p>
                </div>
                <div style="text-align: right;">
                    <span class="meta-deadline">${deadlineLabel}</span>
                    <span class="meta-status ${statusClass}">${statusTexto}</span>
                </div>
            </div>
            <div class="meta-progress-bar">
                <div class="meta-progress-fill" style="width: ${progresso}%;"></div>
            </div>
            <div class="meta-progress-values">
                <span>${formatCurrency(meta.valorAtual)} / ${formatCurrency(
      meta.valorAlvo
    )}</span>
                <span>${progresso}%</span>
            </div>
        `;

    const actionsRow = document.createElement("div");
    actionsRow.className = "meta-actions-row";

    // Botão de reserva (sempre presente para metas não concluídas e não canceladas)
    if (!concluida && !arquivada && meta.status === "ATIVA") {
      const reservaButton = document.createElement("button");
      reservaButton.type = "button";
      reservaButton.className = "btn-primary btn-small";
      reservaButton.dataset.action = "abrir-reserva";
      reservaButton.dataset.metaId = meta.id;
      reservaButton.textContent = "Registrar reserva";
      actionsRow.appendChild(reservaButton);
    }

  // Adicionar botões de gestão específicos do status
  adicionarBotoesGestaoMeta(actionsRow, meta, arquivada, concluida);
    
    card.appendChild(actionsRow);

    card.innerHTML += `
        <p class="meta-reservas-title">Reservas registradas</p>
      `;

    const reservasList = document.createElement("ul");
    reservasList.className = "meta-reservas-list";
    reservasList.dataset.metaId = meta.id;

    if (meta.reservas && meta.reservas.length) {
      meta.reservas.forEach((reserva) => {
        reservasList.appendChild(buildReservaItem(meta, reserva));
      });
    } else {
      const vazio = document.createElement("li");
      vazio.className = "meta-reserva-item meta-reserva-empty";
      vazio.dataset.metaId = meta.id;
      vazio.textContent = "Nenhuma reserva registrada nesta sessão.";
      reservasList.appendChild(vazio);
    }

    card.appendChild(reservasList);
    return card;
  }

  function criarBotaoAcao({ texto, classe, action, metaId }) {
    const botao = document.createElement("button");
    botao.type = "button";
    botao.className = `${classe} btn-small`;
    botao.dataset.action = action;
    botao.dataset.metaId = metaId;
    botao.textContent = texto;
    return botao;
  }

  function adicionarBotoesGestaoMeta(actionsRow, meta, arquivada, concluida) {
    if (arquivada) {
      const label = document.createElement("span");
      label.className =
        meta.status === "CANCELADA" ? "meta-status-cancelada" : "meta-status-info";
      label.textContent =
        meta.status === "CANCELADA" ? "Meta cancelada" : "Meta finalizada";
      actionsRow.appendChild(label);
      return;
    }

    if (meta.status === "CONCLUIDA" || concluida) {
      actionsRow.appendChild(
        criarBotaoAcao({
          texto: "Ver detalhes",
          classe: "btn-secondary",
          action: "detalhes-meta",
          metaId: meta.id,
        })
      );

      if (!meta.finalizada && !meta.finalizadaEm) {
        actionsRow.appendChild(
          criarBotaoAcao({
            texto: "Registrar uso",
            classe: "btn-primary",
            action: "registrar-uso-meta",
            metaId: meta.id,
          })
        );
        actionsRow.appendChild(
          criarBotaoAcao({
            texto: "Liberar saldo",
            classe: "btn-danger",
            action: "liberar-saldo-meta",
            metaId: meta.id,
          })
        );
      } else {
        const label = document.createElement("span");
        label.className = "meta-status-info";
        label.textContent = "Meta finalizada";
        actionsRow.appendChild(label);
      }
      return;
    }

    if (meta.status === "CANCELADA") {
      const label = document.createElement("span");
      label.className = "meta-status-cancelada";
      label.textContent = "Meta cancelada";
      actionsRow.appendChild(label);
      return;
    }

    if (meta.status === "ATIVA" || meta.status === "PAUSADA") {
      actionsRow.appendChild(
        criarBotaoAcao({
          texto: "Editar",
          classe: "btn-secondary",
          action: "editar-meta",
          metaId: meta.id,
        })
      );
      actionsRow.appendChild(
        criarBotaoAcao({
          texto: meta.status === "PAUSADA" ? "Retomar" : "Pausar",
          classe: meta.status === "PAUSADA" ? "btn-success" : "btn-warning",
          action: meta.status === "PAUSADA" ? "retomar-meta" : "pausar-meta",
          metaId: meta.id,
        })
      );
      actionsRow.appendChild(
        criarBotaoAcao({
          texto: "Cancelar",
          classe: "btn-danger",
          action: "cancelar-meta",
          metaId: meta.id,
        })
      );
      actionsRow.appendChild(
        criarBotaoAcao({
          texto: "Concluir",
          classe: "btn-primary",
          action: "concluir-meta",
          metaId: meta.id,
        })
      );
    }
  }

  function buildReservaItem(meta, reserva) {
    const item = document.createElement("li");
    item.className = "meta-reserva-item";
    item.dataset.metaId = meta.id;
    item.dataset.reservaId = reserva.id;

    const info = document.createElement("div");
    info.className = "meta-reserva-info";

    const valorSpan = document.createElement("span");
    valorSpan.className = "meta-reserva-valor";
    valorSpan.textContent = formatCurrency(reserva.valor);

    const dataSpan = document.createElement("span");
    dataSpan.textContent = formatDateTimeValue(
      reserva.criado_em || reserva.atualizado_em
    );

    info.append(valorSpan, dataSpan);
    item.appendChild(info);

    if (reserva.observacao) {
      const obs = document.createElement("p");
      obs.className = "meta-reserva-obs";
      obs.textContent = reserva.observacao;
      item.appendChild(obs);
    }

    const actions = document.createElement("div");
    actions.className = "meta-reserva-actions";

    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.className = "btn-inline";
    editButton.dataset.action = "editar-reserva";
    editButton.dataset.metaId = meta.id;
    editButton.dataset.reservaId = reserva.id;
    editButton.textContent = "Editar";

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "btn-inline btn-danger";
    deleteButton.dataset.action = "excluir-reserva";
    deleteButton.dataset.metaId = meta.id;
    deleteButton.dataset.reservaId = reserva.id;
    deleteButton.textContent = "Excluir";

    actions.append(editButton, deleteButton);
    item.appendChild(actions);

    return item;
  }

  function abrirModalReserva(metaId, modo, reservaId = null) {
    const meta = metasState.get(metaId);
    if (!meta || !modalReserva) {
      showFeedback("Meta não encontrada.", "error");
      return;
    }

    reservaModalMode = modo;
    modalReserva.classList.remove("hidden");
    modalReservaTitulo.textContent =
      modo === "create" ? "Registrar reserva" : "Editar reserva";
    modalReservaMeta.textContent = `${meta.nome} • Progresso ${formatCurrency(
      meta.valorAtual
    )} de ${formatCurrency(meta.valorAlvo)}`;

    inputReservaMetaId.value = metaId;
    inputReservaId.value = reservaId || "";
    inputReservaValor.value = "";
    inputReservaObservacao.value = "";

    if (modo === "edit" && reservaId) {
      const reserva = (meta.reservas || []).find(
        (item) => item.id === reservaId
      );
      if (reserva) {
        inputReservaValor.value = reserva.valor;
        inputReservaObservacao.value = reserva.observacao || "";
      }
      btnSalvarReserva.textContent = "Atualizar";
    } else {
      btnSalvarReserva.textContent = "Salvar";
    }

    btnSalvarReserva.disabled = false;
    setTimeout(() => inputReservaValor.focus(), 0);
  }

  function fecharModalReserva() {
    if (!modalReserva) return;
    modalReserva.classList.add("hidden");
    formReserva?.reset();
    inputReservaMetaId.value = "";
    inputReservaId.value = "";
    btnSalvarReserva.textContent = "Salvar";
    reservaModalMode = "create";
  }

  function abrirModalExclusao(metaId, reservaId) {
    if (!modalConfirmReserva) return;
    const meta = metasState.get(metaId);
    const reserva = meta?.reservas?.find((item) => item.id === reservaId);

    reservaParaExcluir = { metaId, reservaId };
    confirmText.textContent = reserva
      ? `Remover reserva de ${formatCurrency(reserva.valor)} da meta "${
          meta?.nome
        }"?`
      : "Tem certeza que deseja remover esta reserva?";

    modalConfirmReserva.classList.remove("hidden");
  }

  function fecharModalExclusao() {
    if (!modalConfirmReserva) return;
    modalConfirmReserva.classList.add("hidden");
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
      status: "ATIVA",
      finalizada: false,
      finalizadaEm: null,
      valorUtilizado: 0,
      saldoRestante: 0,
      reservas: [],
    });
    renderMetas();
  }

  function editarMeta(meta) {
    abrirModalEditar(meta);
  }

  function pausarMeta(meta) {
    if (!meta) return;
    abrirModalConfirmacao({
      title: "Pausar meta",
      message: `Ao pausar a meta "${meta.nome}", novas reservas ficarão bloqueadas. O progresso atual de ${formatCurrency(
        meta.valorAtual
      )} será preservado e poderá ser retomado futuramente.`,
      confirmLabel: "Pausar meta",
      variant: "warning",
      onConfirm: async () => {
        const response = await fetch(`${API_URL}/metas/meta/${meta.id}/pausar`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data?.erro || "Erro ao pausar meta.");
        }
        showFeedback(data?.mensagem || "Meta pausada com sucesso!", "success");
        await carregarMetas();
      },
    });
  }

  function retomarMeta(meta) {
    if (!meta) return;
    abrirModalConfirmacao({
      title: "Retomar meta",
      message: `A meta "${meta.nome}" voltará a receber reservas normalmente. O progresso acumulado continuará em ${formatCurrency(
        meta.valorAtual
      )}.`,
      confirmLabel: "Retomar meta",
      variant: "success",
      onConfirm: async () => {
        const response = await fetch(`${API_URL}/metas/meta/${meta.id}/retomar`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data?.erro || "Erro ao retomar meta.");
        }
        showFeedback(data?.mensagem || "Meta retomada com sucesso!", "success");
        await carregarMetas();
      },
    });
  }

  function cancelarMeta(meta) {
    if (!meta) return;
    abrirModalCancelar(meta);
  }

  function concluirMeta(meta) {
    if (!meta) return;
    abrirModalConfirmacao({
      title: "Concluir meta",
      message: `Deseja marcar a meta "${meta.nome}" como concluída? Você poderá registrar como o valor foi utilizado em seguida.`,
      confirmLabel: "Concluir meta",
      variant: "success",
      onConfirm: async () => {
        const resposta = await api.concluirMeta(meta.id);
        atualizarEstadoMeta(meta.id, {
          status: "CONCLUIDA",
          concluida_em: resposta?.concluida_em,
          esta_concluida: true,
        });
        await carregarMetas();
        const metaConcluida = metasState.get(meta.id);
        if (metaConcluida) {
          celebrarConclusao(metaConcluida);
        }
      },
    });
  }

  function liberarSaldoMeta(meta) {
    if (!meta) return;
    const valorAtual = Number(meta.valorAtual || 0);
    const valorUtilizado = Math.abs(Number(meta.valorUtilizado || 0));
    const saldoCalculado = Math.max(0, valorAtual - valorUtilizado);
    const saldoExibicao = formatCurrency(saldoCalculado);
    abrirModalConfirmacao({
      title: "Liberar saldo",
      message: `Confirma liberar ${saldoExibicao} da meta "${meta.nome}"? Essa ação finaliza a meta e move o histórico para as metas arquivadas.`,
      confirmLabel: "Liberar saldo",
      variant: "danger",
      onConfirm: async () => {
        const resposta = await api.liberarSaldoMeta(meta.id);
        metaDetalhesCache.delete(meta.id);
        const detalhesAtualizados = await carregarDetalhesMeta(meta.id, false);
        if (metaEmDetalhe && metaEmDetalhe.id === meta.id && detalhesAtualizados) {
          const metaAtualizada = metasState.get(meta.id);
          if (metaAtualizada) {
            metaEmDetalhe = metaAtualizada;
            preencherDetalhesMetaView(metaAtualizada, detalhesAtualizados);
          }
        }
        await carregarMetas();
        showFeedback(
          resposta?.mensagem || "Saldo liberado com sucesso!",
          "success"
        );
      },
    });
  }

  function processarAcaoMeta(event) {
    const trigger = event.target.closest("[data-action]");
    if (!trigger) return;

    const action = trigger.dataset.action;
    const metaId = trigger.dataset.metaId;
    if (!action || !metaId) return;

    const meta = metasState.get(metaId);

    switch (action) {
      case "abrir-reserva":
        abrirModalReserva(metaId, "create");
        break;
      case "editar-reserva": {
        const reservaId = trigger.dataset.reservaId;
        abrirModalReserva(metaId, "edit", reservaId);
        break;
      }
      case "excluir-reserva": {
        const reservaId = trigger.dataset.reservaId;
        abrirModalExclusao(metaId, reservaId);
        break;
      }
      case "editar-meta":
        if (meta) editarMeta(meta);
        else showFeedback("Meta não encontrada.", "error");
        break;
      case "pausar-meta":
        if (meta) pausarMeta(meta);
        else showFeedback("Meta não encontrada.", "error");
        break;
      case "retomar-meta":
        if (meta) retomarMeta(meta);
        else showFeedback("Meta não encontrada.", "error");
        break;
      case "cancelar-meta":
        if (meta) cancelarMeta(meta);
        else showFeedback("Meta não encontrada.", "error");
        break;
      case "concluir-meta":
        if (meta) concluirMeta(meta);
        else showFeedback("Meta não encontrada.", "error");
        break;
      case "detalhes-meta":
        if (meta) abrirDetalhesMeta(meta);
        else showFeedback("Meta não encontrada.", "error");
        break;
      case "registrar-uso-meta":
        if (meta) abrirModalRegistrarUso(meta);
        else showFeedback("Meta não encontrada.", "error");
        break;
      case "liberar-saldo-meta":
        if (meta) liberarSaldoMeta(meta);
        else showFeedback("Meta não encontrada.", "error");
        break;
      default:
        break;
    }
  }

  // Event Listeners
  metasContainer?.addEventListener("click", processarAcaoMeta);
  metasConcluidasContainer?.addEventListener("click", processarAcaoMeta);

  btnFecharDetalhesMeta?.addEventListener("click", () => {
    fecharModalDetalhesMeta();
  });

  modalDetalhesMeta?.addEventListener("click", (event) => {
    if (event.target === modalDetalhesMeta) {
      fecharModalDetalhesMeta();
    }
  });

  btnRegistrarUsoMeta?.addEventListener("click", () => {
    if (!metaEmDetalhe) return;
    abrirModalRegistrarUso(metaEmDetalhe);
  });

  btnLiberarSaldoMeta?.addEventListener("click", () => {
    if (!metaEmDetalhe) return;
    liberarSaldoMeta(metaEmDetalhe);
  });

  btnCancelarRegistrarUso?.addEventListener("click", (event) => {
    event.preventDefault();
    fecharModalRegistrarUso();
  });

  modalRegistrarUso?.addEventListener("click", (event) => {
    if (event.target === modalRegistrarUso) {
      fecharModalRegistrarUso();
    }
  });

  registrarUsoSelect?.addEventListener("change", () => {
    if (!detalhesMetaAtual) {
      btnConfirmarRegistrarUso.disabled = true;
      return;
    }

    const transacaoIdSelecionada = registrarUsoSelect.value;
    if (!transacaoIdSelecionada) {
      preencherPainelUso(detalhesMetaAtual);
      btnConfirmarRegistrarUso.disabled = true;
      return;
    }

    const transacaoSelecionada = (transacoesCache || []).find(
      (item) => String(item.id) === String(transacaoIdSelecionada)
    );

    if (!transacaoSelecionada) {
      preencherPainelUso(detalhesMetaAtual);
      btnConfirmarRegistrarUso.disabled = true;
      return;
    }

    preencherPainelUso(detalhesMetaAtual, transacaoSelecionada);
    btnConfirmarRegistrarUso.disabled = false;
  });

  formRegistrarUso?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!metaParaRegistrarUso) {
      showFeedback(
        "Meta não encontrada para registrar o uso.",
        "error"
      );
      return;
    }

    if (!registrarUsoSelect) {
      showFeedback("Selecione uma despesa para registrar o uso.", "error");
      return;
    }

    const transacaoIdSelecionada = registrarUsoSelect.value;
    if (!transacaoIdSelecionada) {
      showFeedback("Selecione uma despesa para registrar o uso.", "error");
      return;
    }

    try {
      btnConfirmarRegistrarUso.disabled = true;
      btnConfirmarRegistrarUso.textContent = "Registrando...";

      const resposta = await api.registrarUsoMeta(
        metaParaRegistrarUso.id,
        transacaoIdSelecionada
      );

      metaDetalhesCache.delete(metaParaRegistrarUso.id);
      const detalhesAtualizados = await carregarDetalhesMeta(
        metaParaRegistrarUso.id,
        false
      );

      if (
        metaEmDetalhe &&
        metaEmDetalhe.id === metaParaRegistrarUso.id &&
        detalhesAtualizados
      ) {
        const metaAtualizada = metasState.get(metaParaRegistrarUso.id);
        if (metaAtualizada) {
          metaEmDetalhe = metaAtualizada;
          preencherDetalhesMetaView(metaAtualizada, detalhesAtualizados);
        }
      }

      await carregarMetas();

      showFeedback(
        resposta?.mensagem || "Uso registrado com sucesso!",
        "success"
      );

      fecharModalRegistrarUso();
    } catch (error) {
      console.error(error);
      showFeedback(
        error.message || "Não foi possível registrar o uso da meta.",
        "error"
      );
    } finally {
      btnConfirmarRegistrarUso.textContent = "Registrar uso";
      if (modalRegistrarUso?.classList.contains("hidden")) {
        btnConfirmarRegistrarUso.disabled = true;
      } else {
        btnConfirmarRegistrarUso.disabled = false;
      }
    }
  });

  btnCancelarReserva?.addEventListener("click", (event) => {
    event.preventDefault();
    fecharModalReserva();
  });

  modalReserva?.addEventListener("click", (event) => {
    if (event.target === modalReserva) {
      fecharModalReserva();
    }
  });

  btnCancelarReservaExclusao?.addEventListener("click", (event) => {
    event.preventDefault();
    fecharModalExclusao();
  });

  modalConfirmReserva?.addEventListener("click", (event) => {
    if (event.target === modalConfirmReserva) {
      fecharModalExclusao();
    }
  });

  btnCancelarEdicaoMeta?.addEventListener("click", (event) => {
    event.preventDefault();
    fecharModalEditar();
  });

  modalEditarMeta?.addEventListener("click", (event) => {
    if (event.target === modalEditarMeta) {
      fecharModalEditar();
    }
  });

  formEditarMeta?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!metaEmEdicao) {
      showFeedback("Meta não encontrada para edição.", "error");
      return;
    }

    const nome = editarMetaNomeInput.value.trim();
    const valor = Number(editarMetaValorInput.value);
    const dataLimite = editarMetaDataInput.value;

    if (!nome) {
      showFeedback("Informe um nome válido para a meta.", "error");
      return;
    }
    if (Number.isNaN(valor) || valor <= 0) {
      showFeedback("Informe um valor alvo maior que zero.", "error");
      return;
    }
    if (!dataLimite) {
      showFeedback("Selecione uma data limite futura.", "error");
      return;
    }

    const dataSelecionada = new Date(`${dataLimite}T00:00:00`);
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    if (dataSelecionada <= hoje) {
      showFeedback("A data limite deve ser futura.", "error");
      return;
    }

    const metaId = metaEmEdicao.id;

    try {
      btnSalvarEdicaoMeta.disabled = true;
      btnSalvarEdicaoMeta.textContent = "Salvando...";

      const response = await fetch(`${API_URL}/metas/meta/${metaId}/editar`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nome,
          valor_alvo: valor,
          data_limite: dataLimite,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.erro || "Não foi possível editar a meta.");
      }

      const perfilNome = metaEmEdicao.perfilNome || "";
      atualizarEstadoMeta(metaId, data, perfilNome);
      renderMetas();
      fecharModalEditar();
      showFeedback(data?.mensagem || "Meta editada com sucesso!", "success");
    } catch (error) {
      console.error(error);
      showFeedback(error.message || "Não foi possível editar a meta.", "error");
    } finally {
      btnSalvarEdicaoMeta.disabled = false;
      btnSalvarEdicaoMeta.textContent = "Salvar alterações";
      const metaAtualizada = metasState.get(metaId);
      if (!modalEditarMeta?.classList.contains("hidden")) {
        metaEmEdicao = metaAtualizada;
        if (metaAtualizada) {
          const progressoAtual = calcularProgresso(
            metaAtualizada.valorAtual,
            metaAtualizada.valorAlvo
          );
          editarMetaProgresso.textContent = `Progresso atual: ${formatCurrency(
            metaAtualizada.valorAtual
          )} (${progressoAtual}%)`;
        }
      }
    }
  });

  btnCancelarConfirmMeta?.addEventListener("click", (event) => {
    event.preventDefault();
    fecharModalConfirmacao();
  });

  modalConfirmMeta?.addEventListener("click", (event) => {
    if (event.target === modalConfirmMeta) {
      fecharModalConfirmacao();
    }
  });

  btnConfirmMeta?.addEventListener("click", async () => {
    if (!confirmMetaCallback) {
      fecharModalConfirmacao();
      return;
    }

    try {
      btnConfirmMeta.disabled = true;
      await confirmMetaCallback();
      fecharModalConfirmacao();
    } catch (error) {
      console.error(error);
      showFeedback(error.message || "Não foi possível concluir a ação.", "error");
    } finally {
      btnConfirmMeta.disabled = false;
    }
  });

  formCancelarMeta?.addEventListener("change", (event) => {
    if (event.target.name === "cancelar-acao") {
      atualizarVisibilidadeRealocacao(event.target.value);
    }
  });

  btnCancelarCancelamentoMeta?.addEventListener("click", (event) => {
    event.preventDefault();
    fecharModalCancelar();
  });

  modalCancelarMeta?.addEventListener("click", (event) => {
    if (event.target === modalCancelarMeta) {
      fecharModalCancelar();
    }
  });

  formCancelarMeta?.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!metaParaCancelar) {
      showFeedback("Meta não encontrada para cancelamento.", "error");
      return;
    }

    const acaoSelecionada = formCancelarMeta.querySelector(
      'input[name="cancelar-acao"]:checked'
    )?.value;

    if (!acaoSelecionada) {
      showFeedback("Selecione o destino dos fundos antes de cancelar a meta.", "error");
      return;
    }

    let idMetaDestino = null;
    if (acaoSelecionada === "realocar") {
      if (cancelarMetaDestinoSelect?.disabled) {
        showFeedback(
          "Não há metas ativas disponíveis para realocação no momento.",
          "warning"
        );
        return;
      }
      idMetaDestino = cancelarMetaDestinoSelect?.value;
      if (!idMetaDestino) {
        showFeedback(
          "Selecione a meta que receberá os recursos realocados.",
          "error"
        );
        return;
      }
    }

    try {
      btnConfirmarCancelamentoMeta.disabled = true;
      btnConfirmarCancelamentoMeta.textContent = "Cancelando...";

      const response = await fetch(`${API_URL}/metas/meta/${metaParaCancelar.id}/cancelar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          acao_fundos: acaoSelecionada,
          id_meta_destino: idMetaDestino,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.erro || "Não foi possível cancelar a meta.");
      }

      showFeedback(data?.mensagem || "Meta cancelada com sucesso!", "success");
      await carregarMetas();
      fecharModalCancelar();
    } catch (error) {
      console.error(error);
      showFeedback(error.message || "Não foi possível cancelar a meta.", "error");
    } finally {
      btnConfirmarCancelamentoMeta.disabled = false;
      btnConfirmarCancelamentoMeta.textContent = "Cancelar meta";
    }
  });

  btnConfirmarReservaExclusao?.addEventListener("click", async () => {
    if (!reservaParaExcluir) return;
    const { metaId, reservaId } = reservaParaExcluir;
    try {
      btnConfirmarReservaExclusao.disabled = true;
      const resposta = await api.excluirReserva(reservaId);
      removerReservaDaMeta(metaId, reservaId);
      const metaAtual = metasState.get(metaId);
      atualizarEstadoMeta(metaId, resposta.meta, metaAtual?.perfilNome || "");
      renderMetas();
      showFeedback(
        resposta.mensagem || "Reserva removida com sucesso.",
        "success"
      );
    } catch (error) {
      console.error(error);
      showFeedback(
        error.message || "Não foi possível remover a reserva.",
        "error"
      );
    } finally {
      btnConfirmarReservaExclusao.disabled = false;
      fecharModalExclusao();
    }
  });

  formReserva?.addEventListener("submit", async (event) => {
    event.preventDefault();

    const metaId = inputReservaMetaId.value;
    const valor = Number(inputReservaValor.value);
    const observacao = inputReservaObservacao.value.trim();

    if (!metaId) {
      showFeedback("Selecione uma meta válida.", "error");
      return;
    }
    if (Number.isNaN(valor) || valor <= 0) {
      showFeedback(
        "Informe um valor numérico maior que zero para a reserva.",
        "error"
      );
      return;
    }

    try {
      btnSalvarReserva.disabled = true;
      btnSalvarReserva.textContent =
        reservaModalMode === "create" ? "Salvando..." : "Atualizando...";

      let resposta;
      if (reservaModalMode === "create") {
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
      atualizarEstadoMeta(metaId, resposta.meta, metaAtual?.perfilNome || "");
      if (resposta.reserva) {
        registrarReservaNaMeta(metaId, resposta.reserva);
      }

      renderMetas();
      fecharModalReserva();

      const mensagem =
        resposta.mensagem ||
        (reservaModalMode === "create"
          ? "Reserva registrada com sucesso."
          : "Reserva atualizada com sucesso.");
      showFeedback(mensagem, "success");
    } catch (error) {
      console.error(error);
      showFeedback(
        error.message || "Não foi possível salvar a reserva.",
        "error"
      );
    } finally {
      btnSalvarReserva.disabled = false;
      btnSalvarReserva.textContent =
        reservaModalMode === "create" ? "Salvar" : "Atualizar";
    }
  });

  btnRecarregarMetas?.addEventListener("click", () => {
    carregarMetas();
  });

  btnIrCriarMeta?.addEventListener("click", () => {
    if (!form) return;
    const offsetTop = form.getBoundingClientRect().top + window.scrollY - 80;
    window.scrollTo({ top: offsetTop < 0 ? 0 : offsetTop, behavior: "smooth" });
    nomeInput?.focus();
  });

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    resetFeedback();

    const nome = nomeInput.value.trim();
    const dataValor = dataInput.value;
    const perfilId = perfilSelect.value;

    if (!nome) {
      showFeedback("Informe um nome para a meta.", "error");
      return;
    }

    const valor = valorInput.valueAsNumber;
    if (Number.isNaN(valor) || valor <= 0) {
      showFeedback("Informe um valor numérico maior que zero.", "error");
      return;
    }

    if (!dataValor) {
      showFeedback("Selecione uma data limite para planejar a meta.", "error");
      return;
    }

    const dataSelecionada = new Date(`${dataValor}T00:00:00`);
    const hojeComparacao = new Date();
    hojeComparacao.setHours(0, 0, 0, 0);
    if (dataSelecionada <= hojeComparacao) {
      showFeedback("A data limite deve ser futura.", "error");
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

    const perfilNome = perfilId
      ? perfilSelect.options[perfilSelect.selectedIndex]?.textContent
      : "Não vinculado";

    try {
      btnSubmit.disabled = true;
      btnSubmit.textContent = "Criando...";

      const metaCriada = await api.criarMeta(payload);

      showFeedback(
        "Meta criada com sucesso! Confira o plano sugerido abaixo.",
        "success"
      );
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
      showFeedback(error.message || "Não foi possível criar a meta.", "error");
    } finally {
      btnSubmit.disabled = false;
      btnSubmit.textContent = "Criar meta";
    }
  });

  function preencherSugestoes(meta, perfilNome) {
    if (!meta) return;
    resumoNome.textContent = meta.nome;
    resumoValor.textContent = formatCurrency(meta.valor_alvo);
    resumoData.textContent = formatDateValue(meta.data_limite);
    resumoPerfil.textContent = perfilNome || "Não vinculado";
    if (meta.sugestoes) {
      reservaSemanal.textContent = formatCurrency(meta.sugestoes.semanal);
      reservaMensal.textContent = formatCurrency(meta.sugestoes.mensal);
    }
    sugestoesCard?.classList.remove("hidden");
  }

  // Inicialização
  carregarPerfis();
  carregarMetas();
});