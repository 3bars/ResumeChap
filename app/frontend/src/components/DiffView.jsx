// Renders a unified text diff with basic colorization.
export default function DiffView({ text }) {
  if (!text) return null
  const lines = text.split('\n')
  return (
    <div className="diff">
      {lines.map((line, i) => {
        let cls = ''
        if (line.startsWith('+') && !line.startsWith('+++')) cls = 'add'
        else if (line.startsWith('-') && !line.startsWith('---')) cls = 'del'
        else if (line.startsWith('@@')) cls = 'hunk'
        return (
          <div key={i} className={cls}>
            {line || '\u00a0'}
          </div>
        )
      })}
    </div>
  )
}
