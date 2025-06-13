import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerenciador de Tarefas")
        self.geometry("800x600")
        
        self.db = Database()
        self._projetos_selecionados_ids = {}
        self._tarefas_selecionadas_ids = {}

        self._criar_widgets()
        self._carregar_projetos()

        self.protocol("WM_DELETE_WINDOW", self._fechar_janela)

    def _criar_widgets(self):
      
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        projetos_frame = ttk.Labelframe(main_frame, text="Projetos", padding="10")
        projetos_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tarefas_frame = ttk.Labelframe(main_frame, text="Tarefas do Projeto Selecionado", padding="10")
        tarefas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # --- Widgets de Projetos ---
        self.projetos_listbox = tk.Listbox(projetos_frame, height=15)
        self.projetos_listbox.pack(fill=tk.BOTH, expand=True)
        self.projetos_listbox.bind('<<ListboxSelect>>', self._projeto_selecionado)

        projeto_entry_frame = ttk.Frame(projetos_frame)
        projeto_entry_frame.pack(fill=tk.X, pady=5)
        self.projeto_nome_entry = ttk.Entry(projeto_entry_frame)
        self.projeto_nome_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        projeto_botoes_frame = ttk.Frame(projetos_frame)
        projeto_botoes_frame.pack(fill=tk.X)
        ttk.Button(projeto_botoes_frame, text="Adicionar", command=self._adicionar_projeto).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(projeto_botoes_frame, text="Atualizar", command=self._atualizar_projeto).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(projeto_botoes_frame, text="Excluir", command=self._excluir_projeto).pack(side=tk.LEFT, expand=True, fill=tk.X)

      
        self.tarefas_listbox = tk.Listbox(tarefas_frame, height=15)
        self.tarefas_listbox.pack(fill=tk.BOTH, expand=True)

        tarefa_entry_frame = ttk.Frame(tarefas_frame)
        tarefa_entry_frame.pack(fill=tk.X, pady=5)
        self.tarefa_desc_entry = ttk.Entry(tarefa_entry_frame)
        self.tarefa_desc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(tarefa_entry_frame, text="Adicionar Tarefa", command=self._adicionar_tarefa).pack(side=tk.RIGHT)
        
        tarefa_botoes_frame = ttk.Frame(tarefas_frame)
        tarefa_botoes_frame.pack(fill=tk.X)
        ttk.Button(tarefa_botoes_frame, text="Marcar como Concluída", command=self._marcar_concluida).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(tarefa_botoes_frame, text="Excluir Tarefa", command=self._excluir_tarefa).pack(side=tk.LEFT, expand=True, fill=tk.X)
    
    # --- Lógica de Projetos ---
    def _carregar_projetos(self):
        self.projetos_listbox.delete(0, tk.END)
        self._projetos_selecionados_ids.clear()
        for i, projeto in enumerate(self.db.listar_projetos()):
            self.projetos_listbox.insert(tk.END, projeto[1])
            self._projetos_selecionados_ids[i] = projeto[0]

    def _adicionar_projeto(self):
        nome = self.projeto_nome_entry.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "O nome do projeto não pode estar vazio.")
            return
        if self.db.adicionar_projeto(nome):
            messagebox.showinfo("Sucesso", "Projeto adicionado com sucesso!")
            self.projeto_nome_entry.delete(0, tk.END)
            self._carregar_projetos()
        else:
            messagebox.showerror("Erro", "Um projeto com este nome já existe.")

    def _atualizar_projeto(self):
        selecionado_idx = self.projetos_listbox.curselection()
        if not selecionado_idx:
            messagebox.showwarning("Aviso", "Selecione um projeto para atualizar.")
            return
        id_projeto = self._projetos_selecionados_ids[selecionado_idx[0]]
        novo_nome = self.projeto_nome_entry.get().strip()
        if not novo_nome:
            messagebox.showwarning("Aviso", "O novo nome do projeto não pode estar vazio.")
            return
        
        if self.db.atualizar_projeto(id_projeto, novo_nome):
             messagebox.showinfo("Sucesso", "Projeto atualizado com sucesso!")
             self.projeto_nome_entry.delete(0, tk.END)
             self._carregar_projetos()
        else:
             messagebox.showerror("Erro", "Já existe um projeto com este nome.")

    def _excluir_projeto(self):
        selecionado_idx = self.projetos_listbox.curselection()
        if not selecionado_idx:
            messagebox.showwarning("Aviso", "Selecione um projeto para excluir.")
            return
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este projeto? Todas as suas tarefas também serão excluídas."):
            id_projeto = self._projetos_selecionados_ids[selecionado_idx[0]]
            self.db.excluir_projeto(id_projeto)
            messagebox.showinfo("Sucesso", "Projeto excluído com sucesso!")
            self._carregar_projetos()
            self.tarefas_listbox.delete(0, tk.END)

    
    def _projeto_selecionado(self, event=None):
        if not self.projetos_listbox.curselection():
            return
        selecionado_idx = self.projetos_listbox.curselection()[0]
        id_projeto = self._projetos_selecionados_ids[selecionado_idx]
        self._carregar_tarefas(id_projeto)
    
    def _carregar_tarefas(self, projeto_id):
        self.tarefas_listbox.delete(0, tk.END)
        self._tarefas_selecionadas_ids.clear()
        for i, tarefa in enumerate(self.db.listar_tarefas_por_projeto(projeto_id)):
            display_text = f"[{tarefa[2]}] {tarefa[1]}"
            self.tarefas_listbox.insert(tk.END, display_text)
            self._tarefas_selecionadas_ids[i] = tarefa[0]

    def _adicionar_tarefa(self):
        selecionado_idx = self.projetos_listbox.curselection()
        if not selecionado_idx:
            messagebox.showwarning("Aviso", "Selecione um projeto para adicionar a tarefa.")
            return
        id_projeto = self._projetos_selecionados_ids[selecionado_idx[0]]
        descricao = self.tarefa_desc_entry.get().strip()
        if not descricao:
            messagebox.showwarning("Aviso", "A descrição da tarefa não pode estar vazia.")
            return
        self.db.adicionar_tarefa(descricao, id_projeto)
        self.tarefa_desc_entry.delete(0, tk.END)
        self._carregar_tarefas(id_projeto)
        
    def _marcar_concluida(self):
        selecionado_idx = self.tarefas_listbox.curselection()
        if not selecionado_idx:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para marcar como concluída.")
            return
        id_tarefa = self._tarefas_selecionadas_ids[selecionado_idx[0]]
        self.db.atualizar_status_tarefa(id_tarefa, "Concluída")
        self._projeto_selecionado() 

    def _excluir_tarefa(self):
        selecionado_idx_tarefa = self.tarefas_listbox.curselection()
        if not selecionado_idx_tarefa:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para excluir.")
            return
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta tarefa?"):
            id_tarefa = self._tarefas_selecionadas_ids[selecionado_idx_tarefa[0]]
            self.db.excluir_tarefa(id_tarefa)
            self._projeto_selecionado() 

    def _fechar_janela(self):
        self.db.fechar_conexao()
        self.destroy()
