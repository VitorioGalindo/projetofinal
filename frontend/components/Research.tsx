import React, { useState, useEffect } from 'react';
import { ResearchNote } from '../types';
import { PlusIcon, MagnifyingGlassIcon, TrashIcon } from '../constants';

const Research: React.FC = () => {
    const [notes, setNotes] = useState<ResearchNote[]>([]);
    const [activeNoteId, setActiveNoteId] = useState<number | null>(null);
    const [searchTerm, setSearchTerm] = useState('');

    const activeNote = notes.find(note => note.id === activeNoteId);

    useEffect(() => {
        const loadNotes = async () => {
            try {
                const res = await fetch('/api/research/notes');
                if (res.ok) {
                    const json = await res.json();
                    const data: ResearchNote[] = json.notes;
                    setNotes(data);
                    setActiveNoteId(data[0]?.id ?? null);
                }
            } catch (err) {
                console.error('Failed to load notes', err);
            }
        };
        loadNotes();
    }, []);

    const handleNewNote = async () => {
        try {
            const res = await fetch('/api/research/notes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: 'Nova Anotação', summary: '', content: '' })
            });
            if (res.ok) {
                const json = await res.json();
                const newNote: ResearchNote = json.note;
                setNotes(prev => [newNote, ...prev]);
                setActiveNoteId(newNote.id);
            }
        } catch (err) {
            console.error('Failed to create note', err);
        }
    };

    const handleDeleteNote = async (noteId: number) => {
        try {
            await fetch(`/api/research/notes/${noteId}`, { method: 'DELETE' });
            setNotes(prevNotes => {
                const remaining = prevNotes.filter(note => note.id !== noteId);
                if (activeNoteId === noteId) {
                    setActiveNoteId(remaining[0]?.id ?? null);
                }
                return remaining;
            });
        } catch (err) {
            console.error('Failed to delete note', err);
        }
    };

    const handleUpdateNote = (field: 'title' | 'summary' | 'content', value: string) => {
        if (!activeNoteId) return;
        setNotes(prevNotes => {
            const updated = prevNotes.map(note =>
                note.id === activeNoteId
                    ? { ...note, [field]: value, last_updated: new Date().toISOString() }
                    : note
            );
            const noteToUpdate = updated.find(n => n.id === activeNoteId);
            if (noteToUpdate) {
                fetch(`/api/research/notes/${activeNoteId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(noteToUpdate)
                }).catch(err => console.error('Failed to update note', err));
            }
            return updated;
        });
    };

    const filteredNotes = notes.filter(note =>
        note.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        note.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
        note.content.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString('pt-BR', {
            day: '2-digit', month: 'short', year: 'numeric'
        });
    }

    return (
        <div className="flex h-full bg-slate-800/50 rounded-lg border border-slate-700 overflow-hidden">
            {/* Sidebar de Notas */}
            <div className="w-1/3 max-w-sm border-r border-slate-700 flex flex-col">
                <div className="p-4 border-b border-slate-700 flex items-center justify-between">
                    <h2 className="text-xl font-bold text-white">Pesquisa & Estudos</h2>
                </div>
                <div className="p-4 space-y-4">
                    <button onClick={handleNewNote} className="w-full bg-sky-600 text-white font-semibold py-2 rounded-md hover:bg-sky-500 transition-colors flex items-center justify-center gap-2">
                        <PlusIcon className="w-5 h-5" />
                        Nova Nota
                    </button>
                    <div className="relative">
                        <MagnifyingGlassIcon />
                        <input
                            type="text"
                            placeholder="Buscar notas..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full bg-slate-700 border border-slate-600 rounded-md py-2 pl-10 pr-4 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500"
                        />
                    </div>
                </div>
                <div className="flex-grow overflow-y-auto">
                    {filteredNotes.map(note => (
                        <div
                            key={note.id}
                            onClick={() => setActiveNoteId(note.id)}
                            className={`p-4 cursor-pointer border-l-4 ${activeNoteId === note.id ? 'bg-slate-700/50 border-sky-500' : 'border-transparent hover:bg-slate-700/30'}`}
                        >
                            <h3 className="font-semibold text-white truncate">{note.title}</h3>
                            <p className="text-sm text-slate-400 truncate mt-1">
                                {note.summary || note.content.split('\n')[0] || 'Nenhum conteúdo adicional'}
                            </p>
                            <p className="text-xs text-slate-500 mt-2">{formatDate(note.last_updated)}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Editor Principal */}
            <div className="flex-1 flex flex-col">
                {activeNote ? (
                    <>
                        <div className="p-4 border-b border-slate-700 flex justify-between items-center">
                            <p className="text-sm text-slate-400">Última atualização: {formatDate(activeNote.last_updated)}</p>
                            <button onClick={() => handleDeleteNote(activeNote.id)} className="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-700 rounded-full">
                                <TrashIcon className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="flex-grow flex flex-col overflow-y-auto">
                           <input
                                type="text"
                                value={activeNote.title}
                                onChange={(e) => handleUpdateNote('title', e.target.value)}
                                className="w-full p-4 text-2xl font-bold bg-transparent text-white focus:outline-none placeholder-slate-500"
                                placeholder="Título da nota"
                           />
                           <input
                                type="text"
                                value={activeNote.summary}
                                onChange={(e) => handleUpdateNote('summary', e.target.value)}
                                className="w-full p-4 bg-transparent text-slate-300 focus:outline-none placeholder-slate-500"
                                placeholder="Resumo da nota"
                           />
                           <textarea
                                value={activeNote.content}
                                onChange={(e) => handleUpdateNote('content', e.target.value)}
                                className="w-full h-full flex-grow p-4 bg-transparent text-slate-300 focus:outline-none resize-none placeholder-slate-500"
                                placeholder="Comece a escrever sua análise aqui..."
                           />
                       </div>
                   </>
               ) : (
                    <div className="flex items-center justify-center h-full text-center text-slate-500">
                        <div>
                            <h2 className="text-xl font-semibold">Nenhuma nota selecionada</h2>
                            <p>Selecione uma nota da lista ou crie uma nova para começar.</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Research;
