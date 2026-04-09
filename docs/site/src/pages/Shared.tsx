import { useState, useEffect, useCallback, useMemo } from "react";
import { Link2, Shield, ArrowRight, AlertCircle, RefreshCw, MessageSquarePlus } from "lucide-react";
import NavBar from "@/components/NavBar";
import Footer from "@/components/Footer";
import SEO from "@/components/SEO";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { BlockRenderer, FeedbackSidebar } from "@/components/feedback";
import { parseMarkdownToBlocks, useAnnotation, createAnnotation } from "@/lib/annotation";
import {
  parseHashFragment,
  decompressHashPayload,
  generateWebFeedbackUrl,
} from "@/lib/sharing";
import type { SharePayload } from "@/lib/sharing";

const SHARE_BASE_URL = "https://pilot-shell.com/shared";

/** Check that the browser supports the APIs we need */
function checkBrowserSupport(): string | null {
  if (typeof CompressionStream === "undefined") {
    return "Your browser does not support the required compression API. Please upgrade to Chrome 80+, Firefox 113+, or Safari 16.4+.";
  }
  try {
    new Uint8Array(1).toBase64({ alphabet: "base64url" });
  } catch {
    return "Your browser does not support the required base64 encoding API. Please upgrade to Chrome 128+, Safari 17.4+, or Firefox 133+.";
  }
  return null;
}

/** Extract compressed data from a pasted URL string (any supported format) */
function extractFromPastedUrl(input: string): { data: string } | null {
  const trimmed = input.trim();
  if (!trimmed) return null;
  return parseHashFragment(trimmed);
}

type PageState =
  | { status: "browser-unsupported"; reason: string }
  | { status: "landing" }
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; payload: SharePayload }
  | { status: "feedback-only" };

/** Computed once at module load — stable constant, never changes after page load */
const BROWSER_ERROR = checkBrowserSupport();

export default function Shared() {
  const [pageState, setPageState] = useState<PageState>(
    BROWSER_ERROR ? { status: "browser-unsupported", reason: BROWSER_ERROR } : { status: "landing" }
  );
  const [pasteInput, setPasteInput] = useState("");
  const [authorName, setAuthorName] = useState("Anonymous");
  const [isSending, setIsSending] = useState(false);
  const { toast } = useToast();

  const {
    state: annotationState,
    addAnnotation,
    removeAnnotation,
    updateAnnotation,
  } = useAnnotation();

  const loadFromHashData = useCallback(async (data: string) => {
    setPageState({ status: "loading" });
    try {
      const result = await decompressHashPayload(data);
      if (!result) {
        setPageState({ status: "error", message: "Failed to decompress — the URL may be corrupted or truncated." });
        return;
      }
      if (result.type === "feedback") {
        setPageState({ status: "feedback-only" });
        return;
      }
      setPageState({ status: "ready", payload: result.payload });
    } catch {
      setPageState({ status: "error", message: "Failed to load shared document. The URL may be invalid." });
    }
  }, []);

  // Auto-decode hash fragment on mount
  useEffect(() => {
    if (BROWSER_ERROR) return;
    const hash = window.location.hash;
    if (!hash || hash === "#") return;
    const parsed = parseHashFragment(hash);
    if (parsed?.data) {
      loadFromHashData(parsed.data);
    }
  }, [loadFromHashData]);

  const handlePasteLoad = async () => {
    const extracted = extractFromPastedUrl(pasteInput);
    if (!extracted) {
      toast({ title: "Could not parse URL", description: "Paste the full share URL including the part after #", variant: "destructive" });
      return;
    }
    await loadFromHashData(extracted.data);
  };

  const handleSendFeedback = useCallback(async () => {
    const payload = pageState.status === "ready" ? pageState.payload : null;
    if (!payload || annotationState.annotations.length === 0) return;
    setIsSending(true);
    try {
      const feedbackPayload = {
        annotations: annotationState.annotations,
        author: authorName.trim() || "Anonymous",
        planPath: payload.planPath,
        createdAt: Date.now(),
      };
      const baseUrl = SHARE_BASE_URL;
      const result = await generateWebFeedbackUrl(feedbackPayload, baseUrl);
      if (result) {
        await navigator.clipboard.writeText(result.url);
        toast({ title: "Feedback URL copied!", description: "Share it with the document owner to import your annotations." });
      } else {
        toast({
          title: "Feedback too large",
          description: "Please reduce the number or length of annotations and try again.",
          variant: "destructive",
        });
      }
    } catch {
      toast({ title: "Failed to generate feedback URL", description: "Please try again.", variant: "destructive" });
    } finally {
      setIsSending(false);
    }
  }, [pageState, annotationState.annotations, authorName, toast]);

  const payload = pageState.status === "ready" ? pageState.payload : null;
  const blocks = payload ? parseMarkdownToBlocks(payload.specContent) : [];

  // Merge sharer's original annotations with recipient's new annotations for inline display.
  // Only recipient's annotations go into the feedback URL (handled separately in handleSendFeedback).
  const displayAnnotations = useMemo(
    () => [...(payload?.annotations ?? []), ...annotationState.annotations],
    [payload?.annotations, annotationState.annotations],
  );

  const sharedAt = payload
    ? new Date(payload.createdAt).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" })
    : "";

  const contentLabel = payload?.contentType === "requirement" ? "Requirement" : "Specification";

  return (
    <>
      <SEO
        title={`Shared ${contentLabel} — Pilot Shell`}
        description={`View and annotate a shared ${contentLabel.toLowerCase()} from Pilot Shell. Everything happens in your browser — no data reaches our servers.`}
        canonicalUrl={SHARE_BASE_URL}
      />
      <NavBar />

      <main className="min-h-screen bg-background pt-20 pb-12">
        {/* Browser unsupported */}
        {pageState.status === "browser-unsupported" && (
          <div className="max-w-lg mx-auto px-4 py-16 text-center space-y-4">
            <AlertCircle className="h-12 w-12 text-destructive mx-auto" />
            <h2 className="text-xl font-semibold">Browser not supported</h2>
            <p className="text-sm text-muted-foreground">{pageState.reason}</p>
          </div>
        )}

        {/* Landing state */}
        {pageState.status === "landing" && (
          <div className="max-w-2xl mx-auto px-4 py-12 space-y-6">
            <div className="text-center space-y-3">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-primary/10 mb-2">
                <Shield className="h-7 w-7 text-primary" />
              </div>
              <h1 className="text-2xl font-semibold">View Shared Document</h1>
              <p className="text-sm text-muted-foreground max-w-md mx-auto">
                Paste a share URL from Pilot Shell to view and annotate the document, then send your feedback back.
              </p>
            </div>

            <Card>
              <CardContent className="p-5 space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Share URL</label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={pasteInput}
                      onChange={(e) => setPasteInput(e.target.value)}
                      onKeyDown={(e) => { if (e.key === "Enter") handlePasteLoad(); }}
                      placeholder="Paste pilot-shell.com/shared#... or localhost:41777/#/shared/..."
                      className="flex-1 text-sm rounded border border-input bg-background px-3 py-2 placeholder:text-muted-foreground/60 focus:outline-none focus:ring-1 focus:ring-ring"
                      autoFocus
                    />
                    <Button onClick={handlePasteLoad} disabled={!pasteInput.trim()} className="gap-1.5">
                      <ArrowRight size={15} />
                      Load
                    </Button>
                  </div>
                </div>

                {/* Privacy note */}
                <div className="flex items-start gap-2.5 p-3 rounded-lg bg-muted/50 border border-border/50">
                  <Shield className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
                  <div className="space-y-1">
                    <p className="text-xs font-medium">No data sent to servers</p>
                    <p className="text-xs text-muted-foreground">
                      The content is embedded in the URL fragment, which is never transmitted over the network. Everything is decompressed entirely in your browser.
                    </p>
                  </div>
                </div>

                {/* How it works */}
                <ul className="space-y-1.5">
                  {[
                    "Paste the share URL and click Load",
                    "Read the document and add annotations by clicking the + button on any block",
                    "Click Send Feedback to generate a URL to share back",
                  ].map((step, i) => (
                    <li key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
                      <span className="flex-shrink-0 w-4 h-4 rounded-full bg-primary/15 text-primary text-[9px] font-bold flex items-center justify-center mt-0.5">
                        {i + 1}
                      </span>
                      {step}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Loading */}
        {pageState.status === "loading" && (
          <div className="flex items-center justify-center min-h-[50vh]">
            <div className="text-center space-y-3">
              <div className="h-8 w-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-sm text-muted-foreground">Loading shared document…</p>
            </div>
          </div>
        )}

        {/* Error */}
        {pageState.status === "error" && (
          <div className="max-w-lg mx-auto px-4 py-16 text-center space-y-4">
            <AlertCircle className="h-12 w-12 text-destructive mx-auto" />
            <h2 className="text-xl font-semibold">Failed to load</h2>
            <p className="text-sm text-muted-foreground">{pageState.message}</p>
            <div className="flex gap-2 justify-center">
              <Button variant="outline" onClick={() => setPageState({ status: "landing" })} className="gap-1.5">
                <RefreshCw size={14} />
                Paste URL instead
              </Button>
            </div>
          </div>
        )}

        {/* Feedback-only URL */}
        {pageState.status === "feedback-only" && (
          <div className="max-w-lg mx-auto px-4 py-16 text-center space-y-4">
            <MessageSquarePlus className="h-12 w-12 text-primary mx-auto" />
            <h2 className="text-xl font-semibold">This is a feedback URL</h2>
            <p className="text-sm text-muted-foreground">
              This link contains annotation feedback, not a shared document. Open it in Pilot Shell's Spec view by clicking "Receive Feedback" and pasting this URL.
            </p>
            <Button variant="outline" onClick={() => setPageState({ status: "landing" })} className="gap-1.5">
              <Link2 size={14} />
              Back to landing
            </Button>
          </div>
        )}

        {/* Spec viewer */}
        {pageState.status === "ready" && payload && (
          <div className="flex w-full" style={{ minHeight: "calc(100vh - 5rem)" }}>
            {/* Main content */}
            <div className="flex-1 min-w-0 overflow-y-auto">
              <div className="max-w-4xl mx-auto px-4 py-6 space-y-4">
                {/* Header card */}
                <Card>
                  <CardHeader className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="bg-primary/10 rounded-lg p-2 flex-shrink-0">
                        <Shield className="h-4 w-4 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-semibold">Shared {contentLabel}</span>
                          <Badge variant="secondary" className="text-[10px] h-4 px-1.5">Annotatable</Badge>
                        </div>
                        <div className="flex items-center gap-3 text-xs text-muted-foreground mt-0.5 flex-wrap">
                          {payload.author && (
                            <span>by {payload.author}</span>
                          )}
                          {sharedAt && <span>{sharedAt}</span>}
                          <span className="flex items-center gap-1 text-green-600 dark:text-green-400">
                            <Shield size={10} />
                            No data sent to servers
                          </span>
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                </Card>

                {/* Spec content */}
                <Card>
                  <CardContent className="p-5">
                    <BlockRenderer
                      blocks={blocks}
                      annotations={displayAnnotations}
                      selectedAnnotationId={annotationState.selectedAnnotationId}
                      onSelectAnnotation={() => {}}
                      onQuickAnnotate={(blockId, originalText, text) => {
                        addAnnotation(createAnnotation(blockId, originalText, text));
                      }}
                    />
                  </CardContent>
                </Card>
              </div>
            </div>

            {/* Feedback sidebar */}
            <div
              style={{ width: 280, flexShrink: 0, position: "sticky", top: "5rem", height: "calc(100vh - 5rem)", overflow: "hidden" }}
            >
              <FeedbackSidebar
                sharerAnnotations={payload.annotations}
                recipientAnnotations={annotationState.annotations}
                authorName={authorName}
                onAuthorNameChange={setAuthorName}
                onRemoveAnnotation={removeAnnotation}
                onUpdateAnnotation={(id, text) => updateAnnotation(id, { text })}
                onSendFeedback={handleSendFeedback}
                isSending={isSending}
              />
            </div>
          </div>
        )}
      </main>

      {/* Only show footer in non-viewer states */}
      {pageState.status !== "ready" && <Footer />}
    </>
  );
}
