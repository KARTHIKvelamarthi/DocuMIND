import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const uuid = () => crypto.randomUUID();

const useAppStore = create(
  persist(
    (set, get) => ({
      // ── Auth ──────────────────────────────────────────────
      user: null,
      login:  (username) => set({ user: { username } }),
      logout: () => set({ user: null }),

      // ── Groups ────────────────────────────────────────────
      groups: [],
      selectedGroupId: null,

      createGroup: (name) => {
        const group = { id: uuid(), name, chatIds: [] };
        set((s) => ({ groups: [...s.groups, group] }));
        return group.id;
      },

      renameGroup: (groupId, name) =>
        set((s) => ({
          groups: s.groups.map((g) => (g.id === groupId ? { ...g, name } : g)),
        })),

      deleteGroup: (groupId) =>
        set((s) => ({
          groups: s.groups.filter((g) => g.id !== groupId),
          chats:  s.chats.filter((c) => c.groupId !== groupId),
          selectedGroupId: s.selectedGroupId === groupId ? null : s.selectedGroupId,
          selectedChatId:
            s.chats.find((c) => c.groupId === groupId && c.id === s.selectedChatId)
              ? null
              : s.selectedChatId,
        })),

      selectGroup: (groupId) => set({ selectedGroupId: groupId }),

      // ── Chats ─────────────────────────────────────────────
      chats: [],
      selectedChatId: null,

      createChat: (groupId, name = 'New Chat') => {
        const chat = {
          id: uuid(),
          name,
          groupId,
          messages: [],
          pdfs: [],
          selectedPdfIds: [],
        };
        set((s) => ({
          chats: [...s.chats, chat],
          groups: s.groups.map((g) =>
            g.id === groupId ? { ...g, chatIds: [...g.chatIds, chat.id] } : g
          ),
          selectedChatId: chat.id,
          selectedGroupId: groupId,
        }));
        return chat.id;
      },

      renameChat: (chatId, name) =>
        set((s) => ({
          chats: s.chats.map((c) => (c.id === chatId ? { ...c, name } : c)),
        })),

      deleteChat: (chatId) =>
        set((s) => {
          const chat = s.chats.find((c) => c.id === chatId);
          return {
            chats: s.chats.filter((c) => c.id !== chatId),
            groups: s.groups.map((g) =>
              g.id === chat?.groupId
                ? { ...g, chatIds: g.chatIds.filter((id) => id !== chatId) }
                : g
            ),
            selectedChatId: s.selectedChatId === chatId ? null : s.selectedChatId,
          };
        }),

      selectChat: (chatId) => {
        const chat = get().chats.find((c) => c.id === chatId);
        set({
          selectedChatId: chatId,
          selectedGroupId: chat?.groupId ?? get().selectedGroupId,
        });
      },

      // ── Messages ──────────────────────────────────────────
      addMessage: (chatId, message) =>
        set((s) => ({
          chats: s.chats.map((c) =>
            c.id === chatId ? { ...c, messages: [...c.messages, message] } : c
          ),
        })),

      // ── PDFs ──────────────────────────────────────────────
      addPdf: (chatId, pdf) =>
        set((s) => ({
          chats: s.chats.map((c) => {
            if (c.id !== chatId) return c;
            if (c.pdfs.length >= 2) return c;
            if (c.pdfs.find((p) => p.id === pdf.id)) return c;
            return { ...c, pdfs: [...c.pdfs, pdf] };
          }),
        })),

      removePdf: (chatId, pdfId) =>
        set((s) => ({
          chats: s.chats.map((c) =>
            c.id === chatId
              ? {
                  ...c,
                  pdfs: c.pdfs.filter((p) => p.id !== pdfId),
                  selectedPdfIds: c.selectedPdfIds.filter((id) => id !== pdfId),
                }
              : c
          ),
        })),

      togglePdfSelection: (chatId, pdfId) =>
        set((s) => ({
          chats: s.chats.map((c) => {
            if (c.id !== chatId) return c;
            const selected = c.selectedPdfIds.includes(pdfId)
              ? c.selectedPdfIds.filter((id) => id !== pdfId)
              : [...c.selectedPdfIds, pdfId].slice(-2);
            return { ...c, selectedPdfIds: selected };
          }),
        })),
    }),
    {
      name: 'documind-storage',
      partialize: (s) => ({
        user:            s.user,
        groups:          s.groups,
        chats:           s.chats,
        selectedGroupId: s.selectedGroupId,
        selectedChatId:  s.selectedChatId,
      }),
    }
  )
);

export default useAppStore;
