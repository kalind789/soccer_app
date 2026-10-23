import { useEffect, useRef, type ReactNode } from 'react'

type Props = {
  title: string
  onClose: () => void
  children: ReactNode
}

// A pop-up window. It uses the browser's own <dialog>, which already handles the Escape key,
// keeps keyboard focus inside, and dims the page behind it.
function Modal({ title, onClose, children }: Props) {
  const ref = useRef<HTMLDialogElement>(null)

  useEffect(() => {
    ref.current?.showModal()
  }, [])

  return (
    <dialog
      ref={ref}
      className="modal"
      onClose={onClose} // Escape key.
      onClick={(e) => e.target === ref.current && onClose()} // A click on the dimmed area outside.
    >
      <div className="modal-body">
        <div className="modal-header">
          <h2>{title}</h2>
          <button className="ghost icon" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>
        {children}
      </div>
    </dialog>
  )
}

export default Modal
