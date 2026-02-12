---
paths:
  - "**/*.tsx"
  - "**/*.jsx"
  - "**/*.vue"
  - "**/*.svelte"
---

# Components Standards

**Core Rule:** Build small, focused components with single responsibility. Compose complex UIs from simple pieces.

## Component Design Principles

### Single Responsibility

Each component does one thing well. If you need "and" to describe it, split it.

```tsx
// Three focused components
function UserProfileCard({ user }) { /* display only */ }
function UserEditForm({ user, onSave }) { /* editing only */ }
function UserNotifications({ userId }) { /* notifications only */ }
```

### Composition Over Configuration

Build complex UIs by combining simple components, not by adding props.

```tsx
<Card>
  <Card.Header align="left" color="blue">Title</Card.Header>
  <Card.Body>Content</Card.Body>
  <Card.Footer align="right">Actions</Card.Footer>
</Card>
```

### Minimal Props

Keep props under 5-7. More props = component doing too much.

## Component Interface Design

### Explicit Prop Types

Always define prop types with TypeScript interfaces.

```tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  onClick: () => void
  children: React.ReactNode
}

function Button({
  variant = 'primary',
  size = 'md',
  disabled = false,
  onClick,
  children
}: ButtonProps) {
  // Implementation
}
```

### Sensible Defaults

Provide defaults for optional props. Component should work with minimal configuration.

## State Management

### Keep State Local

State lives in the component that uses it. Only lift state when multiple components need it.

```
Does only this component need the state?
├─ YES → Keep it local with useState/ref
└─ NO → Do multiple children need it?
    ├─ YES → Lift to common parent
    └─ NO → Use global state (context/store)
```

### Avoid Prop Drilling

If passing props through 3+ levels, use composition or context instead.

## Naming Conventions

**Components:** PascalCase, descriptive noun (`Button`, `UserCard`, `SearchInput`)

**Props:** camelCase, descriptive. Boolean props: `is*`, `has*`, `should*`, `can*`

**Event handlers:** `on*` for props, `handle*` for internal functions
```tsx
function Form({ onSubmit }) {
  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(data)
  }
  return <form onSubmit={handleSubmit}>...</form>
}
```

## When to Split Components

Split when:
- Component exceeds 200-300 lines
- Component has multiple responsibilities
- Part of component is reusable elsewhere
- Component has complex conditional rendering
- Testing becomes difficult due to complexity

## Decision Checklist

Before completing component work:

- [ ] Component has single, clear responsibility
- [ ] Props are typed with TypeScript/PropTypes
- [ ] Sensible defaults provided for optional props
- [ ] State is as local as possible
- [ ] Component name clearly describes purpose
- [ ] Internal implementation details are private
- [ ] Component is tested
- [ ] No prop drilling beyond 2 levels
- [ ] Component is under 300 lines (or split if larger)
