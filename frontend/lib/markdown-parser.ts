export interface MessagePart {
    type: 'text' | 'code'
    content: string
    language?: string
}

export function parseMarkdown(content: string): MessagePart[] {
    const parts: MessagePart[] = []
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g

    let lastIndex = 0
    let match

    while ((match = codeBlockRegex.exec(content)) !== null) {
        // Add text before code block
        if (match.index > lastIndex) {
            const textContent = content.substring(lastIndex, match.index).trim()
            if (textContent) {
                parts.push({ type: 'text', content: textContent })
            }
        }

        // Add code block
        parts.push({
            type: 'code',
            content: match[2].trim(),
            language: match[1] || 'sql'
        })

        lastIndex = match.index + match[0].length
    }

    // Add remaining text
    if (lastIndex < content.length) {
        const textContent = content.substring(lastIndex).trim()
        if (textContent) {
            parts.push({ type: 'text', content: textContent })
        }
    }

    return parts.length > 0 ? parts : [{ type: 'text', content }]
}
