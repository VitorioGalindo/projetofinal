import { describe, it, expect, beforeEach, vi } from 'vitest';
import { cvmService } from './cvmService';

describe('cvmService', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.unstubAllGlobals();
  });

  it('getCompanies retorna lista de empresas', async () => {
    const mockCompanies = [{ id: 1, name: 'ACME' }];
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ companies: mockCompanies })
    }));
    const companies = await cvmService.getCompanies();
    expect(companies).toEqual(mockCompanies);
  });

  it('getDocumentTypes retorna lista de categorias', async () => {
    const mockTypes = [{ code: 'CAT', description: 'Categoria' }];
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ document_types: mockTypes })
    }));
    const types = await cvmService.getDocumentTypes();
    expect(types).toEqual(mockTypes);
  });

  it('getDocuments usa endpoint por empresa quando companyId informado', async () => {
    const mockDocs = {
      documents: [{
        id: 1,
        delivery_date: '2024-01-01',
        company_name: 'ACME',
        category: 'Cat',
        title: 'Title',
        download_url: 'http://exemplo'
      }]
    };
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockDocs
    });
    vi.stubGlobal('fetch', fetchMock);
    const result = await cvmService.getDocuments({ companyId: 123 });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/documents/by_company/123')
    );
    expect(result[0]).toMatchObject({
      id: '1',
      company: 'ACME',
      category: 'Cat',
      subject: 'Title',
      link: 'http://exemplo'
    });
  });
});
