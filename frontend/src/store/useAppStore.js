import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const uuid = () => crypto.randomUUID();

// Stable empty references — never recreated, so selector equality checks pass
const EMPTY_GROUPS = [];
const EMPTY_CHATS  = [];

const emptyWorkspace = () => ({
  groups:          EMPTY_GROUPS,
  chats:           EMPTY_CHATS,
  selectedGroupId: null,
  selectedChatId:  null,
});

const withWs = (state, updater) => {
  const username = state.user?.username;
  if (!username) return state;
  const current = state.users[username] ?? emptyWorkspace();
  const patch   = typeof updater === 'function' ? updater(current) : updater;
  return { users: { ...state.users, [username]: { ...current, ...patch } } };
};

const useAppStore = create(
  persist(
    (set, get) => ({
      user:  null,
      users: {},

      // ── Auth ──────────────────────────────────────────────
      login: (username, token) =>
        set((s) => ({
          user:  { username, token },
          users: s.users[username]
            ? s.users
            : { ...s.users, [username]: emptyWorkspace() },
        })),

      logout: () => set({ user: null }),

      // ── Groups ────────────────────────────────────────────
      createGroup: (name) => {
        const group = { id: uuid(), name, chatIds: [] };
        set((s) => withWs(s, (ws) => ({ groups: [...ws.groups, group] })));
        return group.id;
      },

      renameGroup: (groupId, name) =>
        set((s) => withWs(s, (ws) => ({
          groups: ws.groups.map((g) => (g.id === groupId ? { ...g, name } : g)),
        }))),

      deleteGroup: (groupId) =>
        set((s) => withWs(s, (ws) => ({
          groups:          ws.groups.filter((g) => g.id !== groupId),
          chats:           ws.chats.filter((c) => c.groupId !== groupId),
          selectedGroupId: ws.selectedGroupId === groupId ? null : ws.selectedGroupId,
          selectedChatId:
            ws.chats.find((c) => c.groupId === groupId && c.id === ws.selectedChatId)
              ? null : ws.selectedChatId,
        }))),

      selectGroup: (groupId) =>
        set((s) => withWs(s, { selectedGroupId: groupId })),

      // ── Chats ─────────────────────────────────────────────
      createChat: (groupId, name = 'New Chat') => {
        const chat = { id: uuid(), name, groupId, messages: [], pdfs: [], selectedPdfIds: [] };
        set((s) => withWs(s, (ws) => ({
          chats:           [...ws.chats, chat],
          groups:          ws.groups.map((g) =>
            g.id === groupId ? { ...g, chatIds: [...g.chatIds, chat.id] } : g
          ),
          selectedChatId:  chat.id,
          selectedGroupId: groupId,
        })));
        return chat.id;
      },

      renameChat: (chatId, name) =>
        set((s) => withWs(s, (ws) => ({
          chats: ws.chats.map((c) => (c.id === chatId ? { ...c, name } : c)),
        }))),

      deleteChat: (chatId) =>
        set((s) => withWs(s, (ws) => {
          const chat = ws.chats.find((c) => c.id === chatId);
          return {
            chats:  ws.chats.filter((c) => c.id !== chatId),
            groups: ws.groups.map((g) =>
              g.id === chat?.groupId
                ? { ...g, chatIds: g.chatIds.filter((id) => id !== chatId) }
                : g
            ),
            selectedChatId: ws.selectedChatId === chatId ? null : ws.selectedChatId,
          };
        })),

      selectChat: (chatId) =>
        set((s) => {
          const ws   = s.users[s.user?.username] ?? emptyWorkspace();
          const chat = ws.chats.find((c) => c.id === chatId);
          return withWs(s, {
            selectedChatId:  chatId,
            selectedGroupId: chat?.groupId ?? ws.selectedGroupId,
          });
        }),

      // ── Messages ──────────────────────────────────────────
      addMessage: (chatId, message) =>
        set((s) => withWs(s, (ws) => ({
          chats: ws.chats.map((c) =>
            c.id === chatId ? { ...c, messages: [...c.messages, message] } : c
          ),
        }))),

      // ── PDFs ──────────────────────────────────────────────
      addPdf: (chatId, pdf) =>
        set((s) => withWs(s, (ws) => ({
          chats: ws.chats.map((c) => {
            if (c.id !== chatId || c.pdfs.length >= 2) return c;
            if (c.pdfs.find((p) => p.id === pdf.id)) return c;
            return { ...c, pdfs: [...c.pdfs, pdf] };
          }),
        }))),

      removePdf: (chatId, pdfId) =>
        set((s) => withWs(s, (ws) => ({
          chats: ws.chats.map((c) =>
            c.id === chatId
              ? { ...c,
                  pdfs:           c.pdfs.filter((p) => p.id !== pdfId),
                  selectedPdfIds: c.selectedPdfIds.filter((id) => id !== pdfId) }
              : c
          ),
        }))),

      togglePdfSelection: (chatId, pdfId) =>
        set((s) => withWs(s, (ws) => ({
          chats: ws.chats.map((c) => {
            if (c.id !== chatId) return c;
            const sel = c.selectedPdfIds.includes(pdfId)
              ? c.selectedPdfIds.filter((id) => id !== pdfId)
              : [...c.selectedPdfIds, pdfId].slice(-2);
            return { ...c, selectedPdfIds: sel };
          }),
        }))),
    }),
    {
      name:       'documind-storage',
      partialize: (s) => ({ user: s.user, users: s.users }),
    }
  )
);

export default useAppStore;
