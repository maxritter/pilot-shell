import { useState } from "react";
import { Dialog, DialogContent, DialogTitle, DialogDescription } from "@/components/ui/dialog";

interface ImageModalProps {
  src: string;
  inlineSrc?: string;
  alt: string;
  className?: string;
  width?: number;
  height?: number;
  loading?: "eager" | "lazy";
}

const ImageModal = ({
  src,
  inlineSrc,
  alt,
  className = "",
  width,
  height,
  loading = "lazy",
}: ImageModalProps) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        aria-label={`Enlarge image: ${alt}`}
        className="block w-full p-0 m-0 border-0 bg-transparent cursor-pointer hover:opacity-90 transition-opacity"
      >
        <img
          src={inlineSrc ?? src}
          alt={alt}
          className={className}
          loading={loading}
          decoding="async"
          width={width}
          height={height}
        />
      </button>
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-[95vw] max-h-[95vh] p-0 border-0 bg-transparent">
          <DialogTitle className="sr-only">{alt}</DialogTitle>
          <DialogDescription className="sr-only">
            Full-size view. Press Escape or click the image to close.
          </DialogDescription>
          <button
            type="button"
            onClick={() => setIsOpen(false)}
            aria-label="Close image"
            className="block w-full h-full p-0 m-0 border-0 bg-transparent cursor-pointer"
          >
            <img
              src={src}
              alt={alt}
              className="w-full h-full object-contain rounded-lg"
              loading="eager"
              decoding="async"
              width={width}
              height={height}
            />
          </button>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ImageModal;
