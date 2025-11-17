
const API_URL = 'http://localhost:5000/api';

/**
 * Módulo de API para interagir com o backend.
 */
export const api = {
    /**
     * Busca as estatísticas do dashboard (Saldo, Receitas, Despesas).
     */
    getDashboardStats: async () => {
        const response = await fetch(`${API_URL}/transacoes/dashboard/stats`);
        if (!response.ok) throw new Error('Falha ao buscar estatísticas');
        return response.json();
    },

    /**
     * Lança uma nova transação (rápida ou completa).
     * (Backend: POST /api/transacoes/lancar_transacao)
     * @param {FormData} formData - Dados do formulário, incluindo o arquivo
     */
    lancarTransacao: async (formData) => {
        const response = await fetch(`${API_URL}/transacoes/lancar_transacao`, {
            method: 'POST',
            body: formData, 
        });
        if (!response.ok) throw new Error('Falha ao lançar transação');
        return response.json();
    },

    /**
     * Anexa um arquivo a uma transação existente (usado na edição).
     * (Backend: POST /api/transacoes/<id>/anexo)
     * @param {string} transacaoId 
     * @param {FormData} formData 
     */
    anexarRecibo: async (transacaoId, formData) => {
        const response = await fetch(`${API_URL}/transacoes/${transacaoId}/anexo`, {
            method: 'POST',
            body: formData,
        });
        if (!response.ok) throw new Error('Falha ao anexar recibo');
        return response.json();
    },

    /**
     * Busca transações filtradas (Filtros Avançados).
     */
    getInboxFiltrado: async (params) => {
        Object.keys(params).forEach(key => 
            (params[key] === null || params[key] === undefined || params[key] === '') && delete params[key]
        );
        const query = new URLSearchParams(params).toString();
        const response = await fetch(`${API_URL}/transacoes/inbox/filtrar?${query}`);
        if (!response.ok) throw new Error('Falha ao filtrar transações');
        return response.json();
    },

    /**
     * Aplica categoria e perfil em lote.
     */
    categorizarEmMassa: async (ids_transacoes, id_categoria, id_perfil) => {
        const response = await fetch(`${API_URL}/transacoes/inbox/categorizar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids_transacoes, id_categoria, id_perfil }),
        });
        if (!response.ok) throw new Error('Falha ao categorizar em massa');
        return response.json();
    },

    /**
     * ATUALIZA uma transação específica (Botão Editar).
     */
    atualizarTransacao: async (id, payload) => {
        const response = await fetch(`${API_URL}/transacoes/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (!response.ok) throw new Error('Falha ao atualizar transação');
        return response.json();
    },

    /**
     * DELETA uma transação específica (Botão Deletar).
     */
    deletarTransacao: async (id) => {
        const response = await fetch(`${API_URL}/transacoes/${id}`, {
            method: 'DELETE',
        });
        if (!response.ok) throw new Error('Falha ao deletar transação');
        return response.json();
    },

    /**
     * Busca a lista de categorias.
     */
    getCategorias: async () => {
        const response = await fetch(`${API_URL}/data/categorias`);
        if (!response.ok) throw new Error('Falha ao buscar categorias');
        return response.json();
    },

    /**
     * Busca a lista de perfis.
     */
    getPerfis: async () => {
        const response = await fetch(`${API_URL}/data/perfis`);
        if (!response.ok) throw new Error('Falha ao buscar perfis');
        return response.json();
    },

    /**
     * Cria uma nova meta financeira.
     */
    criarMeta: async (payload) => {
        const response = await fetch(`${API_URL}/metas/meta/criar_meta`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data?.erro || 'Falha ao criar meta');
        }
        return data;
    },

    /**
     * Lista metas disponíveis para vinculação de reservas.
     */
    getMetasDisponiveis: async () => {
        const response = await fetch(`${API_URL}/reservas/metas-disponiveis`);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data?.erro || 'Falha ao carregar metas');
        }
        return data;
    },

    /**
     * Cria uma nova reserva associada a uma meta.
     */
    criarReserva: async (payload) => {
        const response = await fetch(`${API_URL}/reservas/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data?.erro || 'Falha ao registrar reserva');
        }
        return data;
    },

    /**
     * Atualiza uma reserva existente.
     */
    atualizarReserva: async (id, payload) => {
        const response = await fetch(`${API_URL}/reservas/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data?.erro || 'Falha ao atualizar reserva');
        }
        return data;
    },

    /**
     * Remove uma reserva existente e recalcula o progresso da meta.
     */
    excluirReserva: async (id) => {
        const response = await fetch(`${API_URL}/reservas/${id}`, {
            method: 'DELETE',
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data?.erro || 'Falha ao remover reserva');
        }
        return data;
    },

    /**
     * Busca mapeamentos salvos para importação.
     */
    getMapeamentosImportacao: async () => {
        const response = await fetch(`${API_URL}/transacoes/importacao/mapeamentos`);
        if (!response.ok) throw new Error('Falha ao carregar mapeamentos');
        return response.json();
    },

    /**
     * --- Busca anexos de uma transação ---
     * (Backend: GET /api/transacoes/<id>/anexos)
     */
    getAnexos: async (transacaoId) => {
        const response = await fetch(`${API_URL}/transacoes/${transacaoId}/anexos`);
        if (!response.ok) throw new Error('Falha ao buscar anexos');
        return response.json();
    },

    /**
     * Importa extratos CSV/OFX.
     */
    importarExtrato: async (formData) => {
        const response = await fetch(`${API_URL}/transacoes/importar_extrato`, {
            method: 'POST',
            body: formData
        });
        if (!response.ok) {
            const erro = await response.json().catch(() => ({ erro: 'Erro na importação' }));
            throw new Error(erro.erro || 'Falha ao importar extrato');
        }
        return response.json();
    }
};
