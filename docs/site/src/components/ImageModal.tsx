import { useState } from "react";
import { Dialog, DialogContent } from "@/components/ui/dialog";

interface ImageModalProps {
  src: string;
  alt: string;
  className?: string;
}

const ImageModal = ({ src, alt, className = "" }: ImageModalProps) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <img
        src={src}
        alt={alt}
        className={`cursor-pointer hover:opacity-90 transition-opacity ${className}`}
        onClick={() => setIsOpen(true)}
      />
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-[95vw] max-h-[95vh] p-0 border-0 bg-transparent">
          <img
            src={src}
            alt={alt}
            className="w-full h-full object-contain rounded-lg"
            onClick={() => setIsOpen(false)}
          />
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ImageModal;
