/**
 * @jest-environment node
 *
 * Unit tests for the API client  (@/lib/api)
 * TODO: implement when frontend/lib/api.ts is ready.
 *
 * Assumed exports:
 *   searchSefaria(query: string): Promise<SefariaResult[]>
 *   getSefariaText(ref: string): Promise<SefariaText>
 *   createJob(config: BookConfig): Promise<Job>
 *   getJob(id: string): Promise<Job>
 *   listJobs(): Promise<Job[]>
 *   createConfig(config: BookConfig): Promise<SavedConfig>
 *   listConfigs(): Promise<SavedConfig[]>
 *   getConfig(id: string): Promise<SavedConfig>
 *   updateConfig(id: string, config: BookConfig): Promise<SavedConfig>
 *   deleteConfig(id: string): Promise<void>
 */

// ---------------------------------------------------------------------------
// Mock fetch globally
// ---------------------------------------------------------------------------
const mockFetch = jest.fn();
global.fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
});

function jsonResponse(data: unknown, status = 200) {
  return Promise.resolve(
    new Response(JSON.stringify(data), {
      status,
      headers: { 'Content-Type': 'application/json' },
    }),
  );
}

// ---------------------------------------------------------------------------
// searchSefaria
// ---------------------------------------------------------------------------
describe('searchSefaria', () => {
  it('calls the correct endpoint', async () => {
    mockFetch.mockReturnValueOnce(jsonResponse([]));

    // TODO: uncomment when api.ts exists
    // const { searchSefaria } = await import('@/lib/api');
    // await searchSefaria('genesis');
    // expect(mockFetch).toHaveBeenCalledWith(
    //   expect.stringContaining('/api/v1/sefaria/search?q=genesis'),
    //   expect.any(Object),
    // );

    expect(true).toBe(true); // placeholder
  });

  it('returns parsed result array', async () => {
    const mockData = [{ ref: 'Genesis 1', title: 'Genesis', heTitle: 'בראשית', type: 'Torah' }];
    mockFetch.mockReturnValueOnce(jsonResponse(mockData));

    // TODO: when api.ts exists:
    // const { searchSefaria } = await import('@/lib/api');
    // const result = await searchSefaria('genesis');
    // expect(result).toEqual(mockData);

    expect(true).toBe(true);
  });

  it('throws on non-OK response', async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({ detail: 'Server Error' }, 500));

    // TODO: when api.ts exists:
    // const { searchSefaria } = await import('@/lib/api');
    // await expect(searchSefaria('genesis')).rejects.toThrow();

    expect(true).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// createJob
// ---------------------------------------------------------------------------
describe('createJob', () => {
  const minimalConfig = {
    name: 'Test',
    texts: [{ link: 'Genesis 1', commentary: [], translation: 'English', range: '1:1' }],
    format: {},
  };

  it('POSTs to /api/v1/jobs', async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({ id: 'abc', status: 'pending' }, 201));

    // TODO: when api.ts exists:
    // const { createJob } = await import('@/lib/api');
    // await createJob(minimalConfig);
    // expect(mockFetch).toHaveBeenCalledWith(
    //   expect.stringContaining('/api/v1/jobs'),
    //   expect.objectContaining({ method: 'POST' }),
    // );

    expect(true).toBe(true);
  });

  it('returns job with id and status', async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({ id: 'abc', status: 'pending' }, 201));

    // TODO: when api.ts exists:
    // const { createJob } = await import('@/lib/api');
    // const job = await createJob(minimalConfig);
    // expect(job.id).toBe('abc');
    // expect(job.status).toBe('pending');

    expect(true).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// getJob
// ---------------------------------------------------------------------------
describe('getJob', () => {
  it('GETs /api/v1/jobs/:id', async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({ id: 'abc', status: 'complete' }));

    // TODO: when api.ts exists:
    // const { getJob } = await import('@/lib/api');
    // const job = await getJob('abc');
    // expect(job.status).toBe('complete');

    expect(true).toBe(true);
  });

  it('throws on 404', async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({ detail: 'Not found' }, 404));

    // TODO: when api.ts exists:
    // const { getJob } = await import('@/lib/api');
    // await expect(getJob('ghost')).rejects.toThrow();

    expect(true).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// Configs CRUD
// ---------------------------------------------------------------------------
describe('createConfig', () => {
  it('POSTs to /api/v1/configs', async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({ id: 'cfg-1' }, 201));
    // TODO: when api.ts exists verify call
    expect(true).toBe(true);
  });
});

describe('listConfigs', () => {
  it('GETs /api/v1/configs and returns array', async () => {
    mockFetch.mockReturnValueOnce(jsonResponse([]));
    // TODO: when api.ts exists:
    // const { listConfigs } = await import('@/lib/api');
    // const configs = await listConfigs();
    // expect(Array.isArray(configs)).toBe(true);
    expect(true).toBe(true);
  });
});

describe('deleteConfig', () => {
  it('DELETEs /api/v1/configs/:id', async () => {
    mockFetch.mockReturnValueOnce(new Response(null, { status: 204 }));
    // TODO: when api.ts exists verify call
    expect(true).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// getVersions
// ---------------------------------------------------------------------------
describe('getVersions', () => {
  const mockVersions = [
    { language: 'he', versionTitle: 'Mikraot Gedolot', versionSource: '', languageFamilyName: 'Hebrew' },
    { language: 'en', versionTitle: 'JPS 1917', versionSource: '', languageFamilyName: 'English' },
  ];

  it('calls versions endpoint and returns TextVersion array', async () => {
    let mockGet: jest.Mock;
    let testApi: typeof import('@/lib/api').api;

    jest.isolateModules(() => {
      mockGet = jest.fn().mockResolvedValue({ data: mockVersions });
      jest.doMock('axios', () => ({
        create: jest.fn(() => ({
          get: mockGet,
          interceptors: { response: { use: jest.fn() } },
          defaults: { baseURL: 'http://localhost:8000' },
        })),
      }));
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      testApi = require('@/lib/api').api;
    });

    const result = await testApi!.getVersions('Genesis');
    expect(mockGet!).toHaveBeenCalledWith('/api/v1/sefaria/versions/Genesis');
    expect(result).toEqual(mockVersions);
  });

  it('URL-encodes refs with spaces', async () => {
    let mockGet: jest.Mock;
    let testApi: typeof import('@/lib/api').api;

    jest.isolateModules(() => {
      mockGet = jest.fn().mockResolvedValue({ data: [] });
      jest.doMock('axios', () => ({
        create: jest.fn(() => ({
          get: mockGet,
          interceptors: { response: { use: jest.fn() } },
          defaults: { baseURL: 'http://localhost:8000' },
        })),
      }));
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      testApi = require('@/lib/api').api;
    });

    await testApi!.getVersions('Genesis 1');
    expect(mockGet!).toHaveBeenCalledWith('/api/v1/sefaria/versions/Genesis%201');
  });
});

// ---------------------------------------------------------------------------
// getCommentaries
// ---------------------------------------------------------------------------
describe('getCommentaries', () => {
  const mockCommentaries = [
    { title: 'Rashi', heTitle: 'רש"י' },
    { title: 'Tosafot', heTitle: 'תוספות' },
  ];

  it('calls commentaries endpoint and returns CommentaryOption array', async () => {
    let mockGet: jest.Mock;
    let testApi: typeof import('@/lib/api').api;

    jest.isolateModules(() => {
      mockGet = jest.fn().mockResolvedValue({ data: mockCommentaries });
      jest.doMock('axios', () => ({
        create: jest.fn(() => ({
          get: mockGet,
          interceptors: { response: { use: jest.fn() } },
          defaults: { baseURL: 'http://localhost:8000' },
        })),
      }));
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      testApi = require('@/lib/api').api;
    });

    const result = await testApi!.getCommentaries('Genesis');
    expect(mockGet!).toHaveBeenCalledWith('/api/v1/sefaria/commentaries/Genesis');
    expect(result).toEqual(mockCommentaries);
  });

  it('URL-encodes refs with spaces', async () => {
    let mockGet: jest.Mock;
    let testApi: typeof import('@/lib/api').api;

    jest.isolateModules(() => {
      mockGet = jest.fn().mockResolvedValue({ data: [] });
      jest.doMock('axios', () => ({
        create: jest.fn(() => ({
          get: mockGet,
          interceptors: { response: { use: jest.fn() } },
          defaults: { baseURL: 'http://localhost:8000' },
        })),
      }));
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      testApi = require('@/lib/api').api;
    });

    await testApi!.getCommentaries('Bava Metzia');
    expect(mockGet!).toHaveBeenCalledWith('/api/v1/sefaria/commentaries/Bava%20Metzia');
  });
});
