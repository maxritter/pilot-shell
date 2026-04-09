import { useReducer, useCallback } from "react";
import type { Annotation } from "./types";

export interface AnnotationState {
  annotations: Annotation[];
  selectedAnnotationId: string | null;
}

export type AnnotationAction =
  | { type: "ADD_ANNOTATION"; annotation: Annotation }
  | { type: "REMOVE_ANNOTATION"; id: string }
  | { type: "UPDATE_ANNOTATION"; id: string; updates: Partial<Pick<Annotation, "text">> }
  | { type: "CLEAR_ALL" }
  | { type: "SELECT_ANNOTATION"; id: string | null }
  | { type: "SET_ANNOTATIONS"; annotations: Annotation[] };

export function initialAnnotationState(): AnnotationState {
  return { annotations: [], selectedAnnotationId: null };
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
      return { ...state, annotations: [...state.annotations, action.annotation] };

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
  setAnnotations: (annotations: Annotation[]) => void;
}

export function useAnnotation(): UseAnnotationReturn {
  const [state, dispatch] = useReducer(annotationReducer, undefined, initialAnnotationState);

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
  const setAnnotations = useCallback((annotations: Annotation[]) => { dispatch({ type: "SET_ANNOTATIONS", annotations }); }, []);

  return {
    state,
    addAnnotation,
    removeAnnotation,
    updateAnnotation,
    clearAll,
    selectAnnotation,
    setAnnotations,
  };
}
