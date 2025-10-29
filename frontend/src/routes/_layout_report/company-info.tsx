import { useState } from "react";
import { type SubmitHandler, useForm } from "react-hook-form";
import {
  Container,
  Heading,
  VStack,
  SegmentGroup,
  HStack,
  Field,
  Input,
  Button,
  Box,
  Text
} from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ReportService } from "@/client/sdk.gen";
import { ReportCreateTaskData, CompanyInfoCreate } from "@/client/types.gen";
import type { ApiError } from "@/client/core/ApiError";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import TaskLoading from "@/components/Report/TaskLoading";

export const Route = createFileRoute("/_layout_report/company-info")({
  component: CompanyInfo,
});

enum CompanyType {
  Startup = "Startup",
  PMI = "PMI",
  Corporate = "Corporate",
}


function CompanyInfo() {
  const [taskId, setTaskId] = useState<string | null>(null);
  const { showSuccessToast } = useCustomToast();
  const queryClient = useQueryClient();

  const bg = "bg.canvas";
  const textMuted = "fg.muted";

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<any>({
    defaultValues: {
      tipo_azienda: CompanyType.PMI,
    },
  });

  const mutation = useMutation({
    mutationFn: (data: CompanyInfoCreate) =>
      ReportService.createTask({ requestBody: data } as ReportCreateTaskData),
    onSuccess: (data) => {
      console.log(data);
      setTaskId(data.id);
      showSuccessToast("Richiesta avviata correttamente. Attendere...");
    },
    onError: (err: ApiError) => {
      handleError(err);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["items"] });
    },
  });

  const onSubmit: SubmitHandler<CompanyInfoCreate> = (data) => {
    mutation.mutate(data);
  };

  return (
    <Box bg={bg} color="fg.default" minH="100vh">
      <Container maxW="6xl" py={12}>
        <Box pb={6}>
          <Heading as="h2" size="2xl" lineHeight="short">
            Sii uno dei primi a provare il nostro servizio esclusivo
          </Heading>
          <Text mt={4} color={textMuted}>
            Ottieni subito un'analisi dettagliata della presenza digitale della
            tua azienda e scopri come migliorare la tua posizione sul mercato o
            scoprire un mercato nuovo adatto a te.
          </Text>
        </Box>

        <form onSubmit={handleSubmit(onSubmit)}>
          {/* Tipo Azienda */}
          <HStack gap="10" my={5}>
            <Field.Root required>
              <Field.Label>
                Tipo Azienda <Field.RequiredIndicator />
              </Field.Label>
              <VStack>
                <SegmentGroup.Root
                  size="lg"
                  defaultValue={CompanyType.PMI}
                  onChange={(event) => {
                    const value =
                      typeof event === "string"
                        ? event
                        : ((event?.target as HTMLInputElement)?.value ??
                          CompanyType.PMI);
                    setValue("tipo_azienda", value as CompanyType);
                  }}
                >
                  <SegmentGroup.Indicator />
                  <SegmentGroup.Items items={Object.values(CompanyType)} />
                </SegmentGroup.Root>
              </VStack>
            </Field.Root>
          </HStack>

          {/* Nome e Settore */}
          <HStack gap="10" width="full" mt={5}>
            <Field.Root required invalid={!!errors.name}>
              <Field.Label>
                Nome Azienda <Field.RequiredIndicator />
              </Field.Label>
              <Input
                placeholder="..."
                variant="subtle"
                {...register("name", { required: "Il nome è obbligatorio" })}
              />
              <Field.ErrorText>{errors.name?.message}</Field.ErrorText>
            </Field.Root>

            <Field.Root required invalid={!!errors.settore}>
              <Field.Label>
                Settore <Field.RequiredIndicator />
              </Field.Label>
              <Input
                placeholder="..."
                variant="subtle"
                {...register("settore", {
                  required: "Il settore è obbligatorio",
                })}
              />
              <Field.ErrorText>{errors.settore?.message}</Field.ErrorText>
            </Field.Root>
          </HStack>

          {/* Nazione e Città */}
          <HStack gap="10" width="full" mt={5}>
            <Field.Root required invalid={!!errors.nazione}>
              <Field.Label>
                Nazione <Field.RequiredIndicator />
              </Field.Label>
              <Input
                placeholder="..."
                variant="subtle"
                {...register("nazione", {
                  required: "La nazione è obbligatoria",
                })}
              />
              <Field.ErrorText>{errors.nazione?.message}</Field.ErrorText>
            </Field.Root>

            <Field.Root required invalid={!!errors.citta}>
              <Field.Label>
                Città <Field.RequiredIndicator />
              </Field.Label>
              <Input
                placeholder="..."
                variant="outline"
                {...register("citta", {
                  required: "La città è obbligatoria",
                })}
              />
              <Field.ErrorText>{errors.citta?.message}</Field.ErrorText>
            </Field.Root>
          </HStack>

          {/* URL LinkedIn e sito */}
          <HStack gap="10" width="full" mt={5}>
            <Field.Root invalid={!!errors.url_linkedin}>
              <Field.Label>Url LinkedIn</Field.Label>
              <Input
                placeholder="https://linkedin.com/company/..."
                variant="subtle"
                {...register("url_linkedin", {
                  pattern: {
                    value: /^https?:\/\/(www\.)?linkedin\.com\/.+$/,
                    message:
                      "Inserisci un URL LinkedIn valido (es. https://linkedin.com/company/...)",
                  },
                })}
              />
              <Field.ErrorText>{errors.url_linkedin?.message}</Field.ErrorText>
            </Field.Root>

            <Field.Root invalid={!!errors.url_sito}>
              <Field.Label>Url Azienda</Field.Label>
              <Input
                placeholder="https://..."
                variant="subtle"
                {...register("url_sito", {
                  pattern: {
                    value: /^https?:\/\/.+/,
                    message:
                      "Inserisci un URL valido (deve iniziare con http o https)",
                  },
                })}
              />
              <Field.ErrorText>{errors.url_sito?.message}</Field.ErrorText>
            </Field.Root>
          </HStack>

          <HStack gap="10" mt={50}>
            <Text color={textMuted} fontSize="md">
              Il processo di generazione del report potrebbe richiedere alcuni
              minuti, ti preghiamo di inserire l'email in questo campo per
              essere avvisato una volta che il report sarà pronto.
            </Text>
          </HStack>

          <HStack gap="10" width="full" my={5}>
            {/* CTA email */}
            <Field.Root invalid={!!errors.cta_email}>
              <Field.Label>
                Email <Field.RequiredIndicator />
              </Field.Label>
              <Input
                placeholder="..."
                variant="subtle"
                {...register("cta_email", {
                  pattern: {
                    value: /^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/,
                    message: "Inserisci un'email valida",
                  },
                })}
              />
              <Field.ErrorText>{errors.cta_email?.message}</Field.ErrorText>
            </Field.Root>
          </HStack>

          {/* Pulsante submit */}
          <HStack justify="flex-end" pt={8}>
            <Button type="submit" colorScheme="blue">
              Genera Report
            </Button>
          </HStack>
        </form>
      </Container>

      {taskId && (<TaskLoading taskId={taskId} isOpen={!!taskId} />)}
    </Box>
  );
}

export default CompanyInfo;
