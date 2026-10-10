"use client";

import React, { useState, useEffect } from "react";
import { PromptTemplate } from "@/lib/types";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { LayoutTemplate, Plus, Edit2, Trash2, Check, AlertCircle } from "lucide-react";

interface TemplateManagerProps {
  onSelectTemplate?: (content: string) => void;
}

export const TemplateManager: React.FC<TemplateManagerProps> = ({ onSelectTemplate }) => {
  const { accessToken } = useAuth();
  const [templates, setTemplates] = useState<PromptTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form modal state
  const [isEditing, setIsEditing] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [templateContent, setTemplateContent] = useState("");

  const loadTemplates = async () => {
    if (!accessToken) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.getTemplates(accessToken);
      setTemplates(res.items);
    } catch (err: any) {
      setError(err.message || "Failed to load prompt templates");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadTemplates();
  }, [accessToken]);

  const handleCreateOrUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !templateContent || !accessToken) return;

    try {
      if (editId) {
        await api.updateTemplate(accessToken, editId, {
          name,
          description: description || undefined,
          template_content: templateContent,
        });
      } else {
        await api.createTemplate(accessToken, {
          name,
          description: description || undefined,
          template_content: templateContent,
        });
      }
      resetForm();
      await loadTemplates();
    } catch (err: any) {
      setError(err.message || "Failed to save template");
    }
  };

  const handleEdit = (tmpl: PromptTemplate) => {
    setEditId(tmpl.id);
    setName(tmpl.name);
    setDescription(tmpl.description || "");
    setTemplateContent(tmpl.template_content);
    setIsEditing(true);
  };

  const handleDelete = async (id: string) => {
    if (!accessToken || !confirm("Are you sure you want to delete this prompt template?")) return;
    try {
      await api.deleteTemplate(accessToken, id);
      await loadTemplates();
    } catch (err: any) {
      setError(err.message || "Failed to delete template");
    }
  };

  const resetForm = () => {
    setIsEditing(false);
    setEditId(null);
    setName("");
    setDescription("");
    setTemplateContent("");
  };

  return (
    <div className="flex-1 p-6 bg-slate-950 overflow-y-auto">
      <div className="max-w-5xl mx-auto space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
              <LayoutTemplate className="text-indigo-400" size={22} />
              <span>Prompt Template Library</span>
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Create reusable prompt templates with variable placeholders like {"{{topic}}"}
            </p>
          </div>
          <button
            onClick={() => {
              resetForm();
              setIsEditing(true);
            }}
            className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium px-4 py-2 rounded-xl flex items-center gap-1.5 transition-colors"
          >
            <Plus size={16} />
            <span>New Template</span>
          </button>
        </div>

        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-2 text-red-400 text-xs">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {/* Create/Edit Form Modal */}
        {isEditing && (
          <form onSubmit={handleCreateOrUpdate} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">
              {editId ? "Edit Prompt Template" : "Create New Prompt Template"}
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Template Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  placeholder="e.g. Code Reviewer"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Description (Optional)</label>
                <input
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Brief explanation of purpose"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">
                Template Content (use {"{{variable}}"} for dynamic inputs)
              </label>
              <textarea
                value={templateContent}
                onChange={(e) => setTemplateContent(e.target.value)}
                required
                rows={4}
                placeholder="Analyze the following {{topic}} code in {{tone}} tone: {{code}}"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 font-mono"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={resetForm}
                className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium px-4 py-2 rounded-xl transition-colors"
              >
                {editId ? "Update Template" : "Save Template"}
              </button>
            </div>
          </form>
        )}

        {/* Templates List */}
        {isLoading ? (
          <div className="text-center py-12 text-slate-500 text-sm">Loading templates...</div>
        ) : templates.length === 0 ? (
          <div className="text-center py-12 bg-slate-900/50 border border-slate-800 rounded-2xl p-8">
            <LayoutTemplate size={32} className="mx-auto text-slate-600 mb-3" />
            <h3 className="text-sm font-semibold text-slate-300">No prompt templates created</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              Create your first reusable prompt template with custom variable placeholders.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {templates.map((tmpl) => (
              <div key={tmpl.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between hover:border-slate-700 transition-colors">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-slate-200 text-sm">{tmpl.name}</h4>
                    <span className="text-[10px] font-mono bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded-full">
                      v{tmpl.version}
                    </span>
                  </div>
                  {tmpl.description && (
                    <p className="text-xs text-slate-400 mb-3">{tmpl.description}</p>
                  )}
                  <pre className="bg-slate-950 p-3 rounded-xl text-xs text-slate-300 font-mono overflow-x-auto whitespace-pre-wrap border border-slate-800/80 mb-4 max-h-32">
                    {tmpl.template_content}
                  </pre>
                </div>

                <div className="flex items-center justify-between border-t border-slate-800/80 pt-3">
                  {onSelectTemplate ? (
                    <button
                      onClick={() => onSelectTemplate(tmpl.template_content)}
                      className="bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-400 border border-indigo-500/30 text-xs font-medium px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5"
                    >
                      <Check size={14} />
                      <span>Use Template</span>
                    </button>
                  ) : <div />}

                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => handleEdit(tmpl)}
                      className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
                      title="Edit template"
                    >
                      <Edit2 size={15} />
                    </button>
                    <button
                      onClick={() => handleDelete(tmpl.id)}
                      className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
                      title="Delete template"
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
