import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import type { Faq } from "@/lib/content";

export default function Questions({ faqs, id = "faq", sunk }: { faqs: Faq[]; id?: string; sunk?: boolean }) {
  return (
    <section id={id} className={`w7-sec${sunk ? " w7-sunk" : ""}`} aria-labelledby={`${id}-h`}>
      <div className="w7-wrap w7-faq">
        <h2 className="w7-h2" id={`${id}-h`}>Questions</h2>
        <Accordion type="multiple" className="w7-faql">
          {faqs.map((faq) => (
            <AccordionItem key={faq.question} value={faq.question}>
              <AccordionTrigger>{faq.question}</AccordionTrigger>
              <AccordionContent>
                <p>{faq.answer}</p>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  );
}
