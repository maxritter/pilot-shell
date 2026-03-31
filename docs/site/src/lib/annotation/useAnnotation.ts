import { useReducer, useCallback, useRef, type RefObject } from "react";
import type { Annotation, PendingSelection } from "./types";

export interface AnnotationState {
  annotations: Annotation[];
  selectedAnnotationId: string | null;
  pendingSelection: PendingSelection | null;
}

export type AnnotationAction =
  | { type: "ADD_ANNOTATION"; annotation: Annotation }
  | { type: "REMOVE_ANNOTATION"; id: string }
  | { type: "UPDATE_ANNOTATION"; id: string; updates: Partial<Pick<Annotation, "text">> }
  | { type: "CLEAR_ALL" }
  | { type: "SET_PENDING_SELECTION"; selection: PendingSelection }
  | { type: "CLEAR_PENDING_SELECTION" }
  | { type: "SELECT_ANNOTATION"; id: string | null }
  | { type: "SET_ANNOTATIONS"; annotations: Annotation[] };

export function initialAnnotationState(): AnnotationState {
  return { annotations: [], selectedAnnotationId: null, pendingSelection: null };
}

export function createAnnotation(
  blockId: string,
  originalText: string,
  text: string,
): Annotation {
  return {
    id: crypto.randomUUID(),
    blockId,
    originalText,
    text,
    createdAt: Date.now(),
  };
}

export function annotationReducer(
  state: AnnotationState,
  action: AnnotationAction,
): AnnotationState {
  switch (action.type) {
    case "ADD_ANNOTATION":
      return { ...state, annotations: [...state.annotations, action.annotation], pendingSelection: null };

    case "REMOVE_ANNOTATION": {
      return {
        ...state,
        annotations: state.annotations.filter((a) => a.id !== action.id),
        selectedAnnotationId: state.selectedAnnotationId === action.id ? null : state.selectedAnnotationId,
      };
    }

    case "UPDATE_ANNOTATION":
      return {
        ...state,
        annotations: state.annotations.map((a) => a.id === action.id ? { ...a, ...action.updates } : a),
      };

    case "CLEAR_ALL":
      return { ...state, annotations: [], selectedAnnotationId: null };

    case "SET_PENDING_SELECTION":
      return { ...state, pendingSelection: action.selection };

    case "CLEAR_PENDING_SELECTION":
      return { ...state, pendingSelection: null };

    case "SELECT_ANNOTATION":
      return { ...state, selectedAnnotationId: action.id };

    case "SET_ANNOTATIONS":
      return { ...state, annotations: action.annotations };

    default:
      return state;
  }
}

export interface UseAnnotationReturn {
  state: AnnotationState;
  addAnnotation: (annotation: Annotation) => void;
  removeAnnotation: (id: string) => void;
  updateAnnotation: (id: string, updates: Partial<Pick<Annotation, "text">>) => void;
  clearAll: () => void;
  selectAnnotation: (id: string | null) => void;
  setPendingSelection: (selection: PendingSelection) => void;
  clearPendingSelection: () => void;
  setAnnotations: (annotations: Annotation[]) => void;
  handleMouseUp: (e: React.MouseEvent) => void;
}

export function useAnnotation(
  containerRef: RefObject<HTMLElement | null>,
): UseAnnotationReturn {
  const [state, dispatch] = useReducer(annotationReducer, undefined, initialAnnotationState);
  const isSelectingRef = useRef(false);

  const addAnnotation = useCallback((annotation: Annotation) => {
    dispatch({ type: "ADD_ANNOTATION", annotation });
  }, []);

  const removeAnnotation = useCallback((id: string) => {
    dispatch({ type: "REMOVE_ANNOTATION", id });
  }, []);

  const updateAnnotation = useCallback((id: string, updates: Partial<Pick<Annotation, "text">>) => {
    dispatch({ type: "UPDATE_ANNOTATION", id, updates });
  }, []);

  const clearAll = useCallback(() => { dispatch({ type: "CLEAR_ALL" }); }, []);
  const selectAnnotation = useCallback((id: string | null) => { dispatch({ type: "SELECT_ANNOTATION", id }); }, []);
  const setPendingSelection = useCallback((selection: PendingSelection) => { dispatch({ type: "SET_PENDING_SELECTION", selection }); }, []);
  const clearPendingSelection = useCallback(() => { dispatch({ type: "CLEAR_PENDING_SELECTION" }); }, []);
  const setAnnotations = useCallback((annotations: Annotation[]) => { dispatch({ type: "SET_ANNOTATIONS", annotations }); }, []);

  const handleMouseUp = useCallback(
    (_e: React.MouseEvent) => {
      requestAnimationFrame(() => {
        const selection = window.getSelection?.();
        if (!selection || selection.isCollapsed || !containerRef.current) {
          clearPendingSelection();
          return;
        }

        const selectedText = selection.toString().trim();
        if (!selectedText) { clearPendingSelection(); return; }

        const anchorNode = selection.anchorNode;
        const focusNode = selection.focusNode;

        const findBlockEl = (node: Node | null): Element | null => {
          let el: Node | null = node;
          while (el && el !== containerRef.current) {
            if (el instanceof Element && el.hasAttribute("data-block-id")) return el;
            el = el.parentNode;
          }
          return null;
        };

        const anchorBlock = findBlockEl(anchorNode);
        const focusBlock = findBlockEl(focusNode);

        if (!anchorBlock || !focusBlock || anchorBlock !== focusBlock) {
          selection.removeAllRanges();
          clearPendingSelection();
          return;
        }

        const blockId = anchorBlock.getAttribute("data-block-id") ?? "";
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        isSelectingRef.current = true;
        setPendingSelection({
          blockId,
          selectedText,
          rect: { top: rect.top, left: rect.left, width: rect.width, height: rect.height },
        });
      });
    },
    [containerRef, clearPendingSelection, setPendingSelection],
  );

  return {
    state,
    addAnnotation,
    removeAnnotation,
    updateAnnotation,
    clearAll,
    selectAnnotation,
    setPendingSelection,
    clearPendingSelection,
    setAnnotations,
    handleMouseUp,
  };
}
