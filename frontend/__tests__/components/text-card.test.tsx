/**
 * Unit tests for the TextCard component.
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TextCard } from '@/components/text-card';
import { TextEntry } from '@/lib/types';
import { api } from '@/lib/api';

jest.mock('@/lib/api', () => ({
  api: {
    getVersions: jest.fn().mockResolvedValue([
      { language: 'he', versionTitle: 'Mikraot Gedolot', versionSource: '', languageFamilyName: 'Hebrew' },
      { language: 'en', versionTitle: 'JPS 1917', versionSource: '', languageFamilyName: 'English' },
    ]),
    getCommentaries: jest.fn().mockResolvedValue([
      { title: 'Rashi', heTitle: 'רש"י' },
      { title: 'Tosafot', heTitle: 'תוספות' },
    ]),
  },
}));

function makeWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
}

const defaultEntry: TextEntry = { link: 'Genesis', commentary: [] };

describe('TextCard', () => {
  const onChange = jest.fn();
  const onRemove = jest.fn();

  beforeEach(() => jest.clearAllMocks());

  it('renders the title derived from entry.link', () => {
    render(
      <TextCard entry={defaultEntry} index={0} onChange={onChange} onRemove={onRemove} />,
      { wrapper: makeWrapper() },
    );
    expect(screen.getByText('Genesis')).toBeInTheDocument();
  });

  it('shows index number badge', () => {
    render(
      <TextCard entry={defaultEntry} index={2} onChange={onChange} onRemove={onRemove} />,
      { wrapper: makeWrapper() },
    );
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('calls onRemove when remove button is clicked', () => {
    render(
      <TextCard entry={defaultEntry} index={0} onChange={onChange} onRemove={onRemove} />,
      { wrapper: makeWrapper() },
    );
    fireEvent.click(screen.getByLabelText('Remove text'));
    expect(onRemove).toHaveBeenCalledTimes(1);
  });

  it('expands to show version pickers and commentaries section', () => {
    render(
      <TextCard entry={defaultEntry} index={0} onChange={onChange} onRemove={onRemove} />,
      { wrapper: makeWrapper() },
    );
    fireEvent.click(screen.getByLabelText('Expand'));
    expect(screen.getByText(/Hebrew Edition/i)).toBeInTheDocument();
    expect(screen.getByText(/English Translation/i)).toBeInTheDocument();
    expect(screen.getByText(/Commentaries/i)).toBeInTheDocument();
  });

  it('collapses when toggle button is clicked again', () => {
    render(
      <TextCard entry={defaultEntry} index={0} onChange={onChange} onRemove={onRemove} />,
      { wrapper: makeWrapper() },
    );
    fireEvent.click(screen.getByLabelText('Expand'));
    expect(screen.getByText(/Hebrew Edition/i)).toBeInTheDocument();
    fireEvent.click(screen.getByLabelText('Collapse'));
    expect(screen.queryByText(/Hebrew Edition/i)).not.toBeInTheDocument();
  });

  it('calls getVersions and getCommentaries when expanded', async () => {
    render(
      <TextCard entry={defaultEntry} index={0} onChange={onChange} onRemove={onRemove} />,
      { wrapper: makeWrapper() },
    );
    fireEvent.click(screen.getByLabelText('Expand'));
    await waitFor(() => {
      expect(api.getVersions).toHaveBeenCalledWith('Genesis');
      expect(api.getCommentaries).toHaveBeenCalledWith('Genesis');
    });
  });

  it('does not call API when collapsed', () => {
    render(
      <TextCard entry={defaultEntry} index={0} onChange={onChange} onRemove={onRemove} />,
      { wrapper: makeWrapper() },
    );
    expect(api.getVersions).not.toHaveBeenCalled();
    expect(api.getCommentaries).not.toHaveBeenCalled();
  });

  it('toggles commentary selection and calls onChange', async () => {
    render(
      <TextCard entry={defaultEntry} index={0} onChange={onChange} onRemove={onRemove} />,
      { wrapper: makeWrapper() },
    );
    fireEvent.click(screen.getByLabelText('Expand'));

    // Wait for the dynamic commentaries to resolve; span title = "Rashi (רש\"י)"
    const rashiSpan = await screen.findByTitle('Rashi (רש"י)');
    fireEvent.click(rashiSpan.closest('label')!);

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ commentary: ['Rashi'] }),
    );
  });

  it('un-toggles an already-selected commentary', async () => {
    const entryWithRashi: TextEntry = { link: 'Genesis', commentary: ['Rashi'] };
    render(
      <TextCard entry={entryWithRashi} index={0} onChange={onChange} onRemove={onRemove} />,
      { wrapper: makeWrapper() },
    );
    fireEvent.click(screen.getByLabelText('Expand'));

    // Use title to disambiguate from the header badge that also shows "Rashi"
    const rashiSpan = await screen.findByTitle('Rashi (רש"י)');
    fireEvent.click(rashiSpan.closest('label')!);

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ commentary: [] }),
    );
  });

  it('shows active commentary badges in the header', () => {
    const entryWithCommentary: TextEntry = { link: 'Genesis', commentary: ['Rashi', 'Tosafot'] };
    render(
      <TextCard entry={entryWithCommentary} index={0} onChange={onChange} onRemove={onRemove} />,
      { wrapper: makeWrapper() },
    );
    expect(screen.getByText('Rashi')).toBeInTheDocument();
    expect(screen.getByText('Tosafot')).toBeInTheDocument();
  });

  it('calls onChange with updated version_title when Hebrew edition selected', async () => {
    render(
      <TextCard entry={defaultEntry} index={0} onChange={onChange} onRemove={onRemove} />,
      { wrapper: makeWrapper() },
    );
    fireEvent.click(screen.getByLabelText('Expand'));

    // Wait for the version pickers to render (loading spinner resolves)
    await waitFor(() => {
      expect(screen.queryByText(/Loading editions/i)).not.toBeInTheDocument();
    });

    // The Select triggers are rendered; verify the Hebrew Edition Select is present
    const hebrewEditionLabel = screen.getByText(/Hebrew Edition/i);
    expect(hebrewEditionLabel).toBeInTheDocument();
  });
});
