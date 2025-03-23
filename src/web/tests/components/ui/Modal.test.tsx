import React from 'react'; // version 18.2.0
import { screen, fireEvent, waitFor } from '@testing-library/react'; // version 14.0.0
import userEvent from '@testing-library/user-event'; // version 14.4.3

import Modal from '../../../src/components/ui/Modal';
import { Size } from '../../../src/types/common';
import { renderWithProviders } from '../../../src/utils/testing';

describe('Modal component', () => {
  it('renders correctly when open', () => {
    const onClose = jest.fn();
    renderWithProviders(<Modal isOpen={true} onClose={onClose} title="Test Modal" ariaLabelledBy="modal-title">
      <div>Test Content</div>
    </Modal>);

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Test Modal')).toBeInTheDocument();
    expect(screen.getByText('Test Content')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Close modal' })).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    const onClose = jest.fn();
    renderWithProviders(<Modal isOpen={false} onClose={onClose} title="Test Modal">
      <div>Test Content</div>
    </Modal>);

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('renders different sizes correctly', () => {
    const onClose = jest.fn();

    renderWithProviders(<Modal isOpen={true} onClose={onClose} size={Size.SMALL} title="Small Modal">
      <div>Small Content</div>
    </Modal>);
    expect(screen.getByRole('dialog')).toHaveClass('modal-sm');

    renderWithProviders(<Modal isOpen={true} onClose={onClose} size={Size.MEDIUM} title="Medium Modal">
      <div>Medium Content</div>
    </Modal>);
    expect(screen.getByRole('dialog')).toHaveClass('modal-md');

    renderWithProviders(<Modal isOpen={true} onClose={onClose} size={Size.LARGE} title="Large Modal">
      <div>Large Content</div>
    </Modal>);
    expect(screen.getByRole('dialog')).toHaveClass('modal-lg');
  });

  it('calls onClose when close button is clicked', () => {
    const onClose = jest.fn();
    renderWithProviders(<Modal isOpen={true} onClose={onClose} title="Test Modal">
      <div>Test Content</div>
    </Modal>);

    const closeButton = screen.getByRole('button', { name: 'Close modal' });
    fireEvent.click(closeButton);

    expect(onClose).toHaveBeenCalled();
  });

  it('calls onClose when clicking outside if closeOnClickOutside is true', () => {
    const onClose = jest.fn();
    renderWithProviders(<Modal isOpen={true} onClose={onClose} closeOnClickOutside={true} title="Test Modal">
      <div>Test Content</div>
    </Modal>);

    fireEvent.mouseDown(screen.getByClassName('modal-container'));

    expect(onClose).toHaveBeenCalled();
  });

  it('does not call onClose when clicking outside if closeOnClickOutside is false', () => {
    const onClose = jest.fn();
    renderWithProviders(<Modal isOpen={true} onClose={onClose} closeOnClickOutside={false} title="Test Modal">
      <div>Test Content</div>
    </Modal>);

    fireEvent.mouseDown(screen.getByClassName('modal-container'));

    expect(onClose).not.toHaveBeenCalled();
  });

  it('calls onClose when pressing Escape if closeOnEscape is true', () => {
    const onClose = jest.fn();
    renderWithProviders(<Modal isOpen={true} onClose={onClose} closeOnEscape={true} title="Test Modal">
      <div>Test Content</div>
    </Modal>);

    fireEvent.keyDown(document.body, { key: 'Escape' });

    expect(onClose).toHaveBeenCalled();
  });

  it('does not call onClose when pressing Escape if closeOnEscape is false', () => {
    const onClose = jest.fn();
    renderWithProviders(<Modal isOpen={true} onClose={onClose} closeOnEscape={false} title="Test Modal">
      <div>Test Content</div>
    </Modal>);

    fireEvent.keyDown(document.body, { key: 'Escape' });

    expect(onClose).not.toHaveBeenCalled();
  });

  it('does not show close button when showCloseButton is false', () => {
    const onClose = jest.fn();
    renderWithProviders(<Modal isOpen={true} onClose={onClose} showCloseButton={false} title="Test Modal">
      <div>Test Content</div>
    </Modal>);

    expect(screen.queryByRole('button', { name: 'Close modal' })).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    const onClose = jest.fn();
    renderWithProviders(<Modal isOpen={true} onClose={onClose} className="custom-modal" title="Test Modal">
      <div>Test Content</div>
    </Modal>);

    expect(screen.getByRole('dialog')).toHaveClass('custom-modal');
  });

  it('has correct accessibility attributes', () => {
    const onClose = jest.fn();
    renderWithProviders(<Modal isOpen={true} onClose={onClose} ariaLabelledBy="modal-title" title="Test Modal">
      <div>Test Content</div>
    </Modal>);

    const modal = screen.getByRole('dialog');
    expect(modal).toHaveAttribute('role', 'dialog');
    expect(modal).toHaveAttribute('aria-modal', 'true');
    expect(modal).toHaveAttribute('aria-labelledby', 'modal-title');

    const closeButton = screen.getByRole('button', { name: 'Close modal' });
    expect(closeButton).toHaveAttribute('aria-label', 'Close modal');
  });

  it('traps focus within the modal', async () => {
    const onClose = jest.fn();
    renderWithProviders(
      <Modal isOpen={true} onClose={onClose} title="Test Modal">
        <div>
          <button>First Focusable</button>
          <input type="text" />
          <button>Last Focusable</button>
        </div>
      </Modal>
    );

    const firstFocusable = screen.getByText('First Focusable');
    const lastFocusable = screen.getByText('Last Focusable');
    expect(firstFocusable).toHaveFocus();

    await userEvent.tab();
    expect(screen.getByRole('textbox')).toHaveFocus();

    await userEvent.tab();
    expect(lastFocusable).toHaveFocus();

    await userEvent.tab();
    expect(firstFocusable).toHaveFocus();
  });

  it('animates when opening and closing', async () => {
    const onClose = jest.fn();
    renderWithProviders(<Modal isOpen={true} onClose={onClose} title="Test Modal">
      <div>Test Content</div>
    </Modal>);

    const modalContainer = screen.getByClassName('modal-container');
    expect(modalContainer).toHaveClass('modal-container--entering');

    await waitFor(() => {
      expect(modalContainer).toHaveClass('modal-container--entered');
    });

    fireEvent.click(screen.getByRole('button', { name: 'Close modal' }));
    expect(modalContainer).toHaveClass('modal-container--exiting');

    await waitFor(() => {
      expect(onClose).toHaveBeenCalled();
    });
  });
});