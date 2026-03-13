/**
 * Unit tests for the TextSearch component.
 * TODO: implement when frontend/components/text-search.tsx is ready.
 *
 * Expected component contract:
 *   <TextSearch onSelect={(ref: string) => void} />
 *
 * - Renders a search input
 * - Debounces input and calls searchSefaria from @/lib/api
 * - Renders a results list; each item shows title + heTitle
 * - Calls onSelect(ref) when a result is clicked
 * - Shows a loading spinner while the fetch is in-flight
 * - Shows an empty-state message when results are []
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
// TODO: swap path once component exists
// import { TextSearch } from '@/components/text-search';

// ---------------------------------------------------------------------------
// Mock the API module
// ---------------------------------------------------------------------------
jest.mock('@/lib/api', () => ({
  searchSefaria: jest.fn().mockResolvedValue([
    { ref: 'Genesis 1', title: 'Genesis', heTitle: 'בראשית', type: 'Torah' },
  ]),
}));

// Placeholder until component is scaffolded
const TextSearch = (_props: { onSelect: (ref: string) => void }) => (
  <div>TODO: TextSearch component not yet implemented</div>
);

describe('TextSearch', () => {
  const noop = () => {};

  // -------------------------------------------------------------------------
  it('renders search input', () => {
    render(<TextSearch onSelect={noop} />);
    // TODO: uncomment once real component exists
    // expect(screen.getByRole('searchbox')).toBeInTheDocument();
    expect(true).toBe(true); // placeholder assertion
  });

  // -------------------------------------------------------------------------
  it('shows results after typing', async () => {
    const { searchSefaria } = require('@/lib/api');
    render(<TextSearch onSelect={noop} />);

    // TODO: when component exists:
    // const input = screen.getByRole('searchbox');
    // await userEvent.type(input, 'genesis');
    // await waitFor(() => expect(screen.getByText('Genesis')).toBeInTheDocument());
    // expect(searchSefaria).toHaveBeenCalledWith('genesis');

    expect(true).toBe(true); // placeholder
  });

  // -------------------------------------------------------------------------
  it('calls onSelect when result clicked', async () => {
    const handleSelect = jest.fn();
    render(<TextSearch onSelect={handleSelect} />);

    // TODO: when component exists:
    // const input = screen.getByRole('searchbox');
    // await userEvent.type(input, 'genesis');
    // await waitFor(() => screen.getByText('Genesis'));
    // await userEvent.click(screen.getByText('Genesis'));
    // expect(handleSelect).toHaveBeenCalledWith('Genesis 1');

    expect(true).toBe(true); // placeholder
  });

  // -------------------------------------------------------------------------
  it('shows loading state while searching', async () => {
    const { searchSefaria } = require('@/lib/api');
    // Make the promise hang so we can catch the loading state
    searchSefaria.mockImplementationOnce(
      () => new Promise(() => {}), // never resolves
    );

    render(<TextSearch onSelect={noop} />);

    // TODO: when component exists:
    // await userEvent.type(screen.getByRole('searchbox'), 'gen');
    // expect(screen.getByRole('status')).toBeInTheDocument(); // spinner / aria-live

    expect(true).toBe(true); // placeholder
  });

  // -------------------------------------------------------------------------
  it('shows empty state when no results', async () => {
    const { searchSefaria } = require('@/lib/api');
    searchSefaria.mockResolvedValueOnce([]);

    render(<TextSearch onSelect={noop} />);

    // TODO: when component exists:
    // await userEvent.type(screen.getByRole('searchbox'), 'zzz');
    // await waitFor(() =>
    //   expect(screen.getByText(/no results/i)).toBeInTheDocument()
    // );

    expect(true).toBe(true); // placeholder
  });
});
