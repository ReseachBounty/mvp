import {
  Box,
  Flex,
  Spinner,
  Text,
  Progress,
  VStack,
} from "@chakra-ui/react";
import { useTheme } from 'next-themes'
import { useEffect, useState } from "react";
import { ReportService } from "@/client";
import { useNavigate } from "@tanstack/react-router";

// Tipi possibili di step
const STEPS = [
  "Analisi delle informazioni",
  "Raggruppamento dei risultati",
  "Creazione del report",
  "Invio del report",
] as const;

type StepType = (typeof STEPS)[number];

interface ProcessOverlayProps {
    taskId: string;
    isOpen: boolean;
}

export default function TaskLoading({
    taskId,
    isOpen,
}: ProcessOverlayProps) {
    const navigate = useNavigate();

  const [currentStep, setCurrentStep] = useState<StepType | null>(null);
  const { theme } = useTheme();
  const overlayBg = theme === 'light' ? "blackAlpha.700" : "blackAlpha.800";

    useEffect(() => {
      if (!isOpen) return;
      let interval: NodeJS.Timeout;

      const fetchStatus = async () => {
        const response = await ReportService.readTask({ taskId });
        return response.status as StepType | "completed";
      };

      const pollStatus = async () => {
        try {
          const status = await fetchStatus();
          if (status === "completed") {
            clearInterval(interval);
            navigate({ to: "/report/$taskId", params: { taskId } });
          } else {
            setCurrentStep(status);
          }
        } catch (err) {
          console.error("Errore durante polling:", err);
        }
      };

      // Poll ogni 2 secondi
      pollStatus();
      interval = setInterval(pollStatus, 2000);

      return () => clearInterval(interval);
    }, [isOpen]);

  if (!isOpen) return null;

  const currentIndex = currentStep
    ? STEPS.findIndex((s) => s === currentStep)
    : 0;

  const progress = ((currentIndex + 1) / STEPS.length) * 100;

  return (
    <Flex
      position="fixed"
      top={0}
      left={0}
      w="100vw"
      h="100vh"
      bg={overlayBg}
      backdropFilter="blur(4px)"
      zIndex={9999}
      align="center"
      justify="center"
    >
      <Box
        bg="white"
        p={8}
        borderRadius="2xl"
        boxShadow="xl"
        w="md"
        textAlign="center"
      >
        <VStack>
          <Spinner size="xl" color="blue.500" />
          <Text fontSize="xl" fontWeight="semibold">
            {currentStep || "Inizio del processo..."}
          </Text>
          <Progress.Root
            value={progress}
            size="sm"
            colorScheme="blue"
            borderRadius="md"
            w="full"
            striped
            animated
          />
          <Text fontSize="sm" color="gray.500">
            {Math.round(progress)}% completed
          </Text>
        </VStack>
      </Box>
    </Flex>
  );
}
