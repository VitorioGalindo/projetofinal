import React, { useEffect, useState } from 'react';
import { CvmDocument, CvmCompany, CvmDocumentType } from '../types';
import { DocumentTextIcon, ChevronDownIcon, ArrowTopRightOnSquareIcon } from '../constants';
import { cvmService } from '../services/cvmService';

interface Option {
    value: string;
    label: string;
}

const FilterDropdown: React.FC<{ label: string; options: Option[]; value: string; onChange: (v: string) => void; className?: string; }> = ({ label, options, value, onChange, className }) => (
    <div>
        <label className="block text-sm font-medium text-slate-400 mb-1">{label}</label>
        <div className="relative">
            <select
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className={`w-full appearance-none bg-slate-700 border border-slate-600 rounded-md py-2 px-3 text-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500 ${className}`}
            >
                {options.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-400">
                <ChevronDownIcon />
            </div>
        </div>
    </div>
);

const parseDateRange = (range: string): [string | undefined, string | undefined] => {
    if (!range) return [undefined, undefined];
    const parts = range.split('–');
    if (parts.length !== 2) return [undefined, undefined];
    const start = parts[0].trim().replace(/\//g, '-');
    const end = parts[1].trim().replace(/\//g, '-');
    return [start, end];
};

const CvmDocuments: React.FC = () => {
    const [companies, setCompanies] = useState<Option[]>([]);
    const [documentTypes, setDocumentTypes] = useState<Option[]>([{ value: '', label: 'Todas' }]);
    const [selectedCompany, setSelectedCompany] = useState<string>('');
    const [selectedDocumentType, setSelectedDocumentType] = useState<string>('');
    const [dateRange, setDateRange] = useState<string>('');
    const [documents, setDocuments] = useState<CvmDocument[]>([]);

    useEffect(() => {
        const loadFilters = async () => {
            const companyData: CvmCompany[] = await cvmService.getCompanies();
            setCompanies([{ value: '', label: 'Todas' }, ...companyData.map(c => ({ value: String(c.id), label: `${c.ticker} - ${c.company_name}` }))]);

            const docTypes: CvmDocumentType[] = await cvmService.getDocumentTypes();
            setDocumentTypes([{ value: '', label: 'Todas' }, ...docTypes.map(dt => ({ value: dt.code, label: dt.name }))]);
        };
        loadFilters();
    }, []);

    useEffect(() => {
        const fetchDocs = async () => {
            const [start, end] = parseDateRange(dateRange);
            const docs = await cvmService.getDocuments({
                companyId: selectedCompany ? Number(selectedCompany) : undefined,
                documentType: selectedDocumentType || undefined,
                startDate: start,
                endDate: end,
                limit: 50,
            });
            setDocuments(docs);
        };
        fetchDocs();
    }, [selectedCompany, selectedDocumentType, dateRange]);

    return (
        <div className="bg-slate-800/50 rounded-lg p-6 md:p-8 space-y-6 border border-slate-700">
            <div className="flex items-center gap-3">
                <DocumentTextIcon className="w-8 h-8 text-sky-400" />
                <h1 className="text-3xl font-bold text-white">Documentos CVM</h1>
            </div>

            <div className="border-b border-slate-700 pb-6">
                <h2 className="text-xl font-semibold text-white mb-4">Filtros</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <FilterDropdown
                        label="Filtrar por Empresa"
                        options={companies}
                        value={selectedCompany}
                        onChange={setSelectedCompany}
                    />
                    <FilterDropdown
                        label="Filtrar por Categoria"
                        options={documentTypes}
                        value={selectedDocumentType}
                        onChange={setSelectedDocumentType}
                    />
                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-1">Filtrar por Período de Publicação</label>
                        <input
                            type="text"
                            value={dateRange}
                            onChange={(e) => setDateRange(e.target.value)}
                            placeholder="YYYY/MM/DD – YYYY/MM/DD"
                            className="w-full bg-slate-700 border border-slate-600 rounded-md py-2 px-3 text-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                        />
                    </div>
                </div>
            </div>

            <div>
                <p className="text-md font-semibold text-white mb-4">
                    Exibindo {documents.length} documentos encontrados
                </p>
                <div className="overflow-x-auto border border-slate-700 rounded-lg">
                    <table className="w-full text-sm text-left">
                        <thead className="bg-slate-700/50 text-xs text-slate-400 uppercase">
                            <tr>
                                {['Data', 'Empresa', 'Categoria', 'Assunto', 'Link'].map(h => (
                                    <th key={h} scope="col" className="px-6 py-3 font-medium tracking-wider">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700">
                            {documents.map((doc) => (
                                <tr key={doc.id} className="hover:bg-slate-700/30">
                                    <td className="px-6 py-4 whitespace-nowrap text-slate-300">{doc.date}</td>
                                    <td className="px-6 py-4 whitespace-nowrap font-medium text-white">{doc.company}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-slate-300">{doc.category}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-slate-300">{doc.subject}</td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <a href={doc.link} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-sky-400 hover:text-sky-300 font-semibold">
                                            Abrir
                                            <ArrowTopRightOnSquareIcon className="w-4 h-4" />
                                        </a>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default CvmDocuments;
