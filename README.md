# Module de Facturation à l'Avancement BTP (Construction Progress Billing)

Ce module Odoo est conçu spécifiquement pour répondre aux besoins de facturation du secteur du bâtiment et de la construction. Il permet de gérer les situations de travaux, les retenues de garantie et le compte prorata directement depuis les commandes de vente.

## Fonctionnalités Principales

*   **Facturation à l'Avancement (Situations)** : Générez des factures basées sur un pourcentage d'avancement des travaux (situations de travaux) plutôt que sur les quantités livrées classiques.
*   **Retenue de Garantie (RG)** : Gestion automatique de la retenue de garantie sur les factures de vente (ex: 5% retenus jusqu'à la réception des travaux).
*   **Compte Prorata** : Gestion des frais de compte prorata à déduire des factures.

## Installation

1.  Assurez-vous que les modules `sale_management` et `account` sont installés.
2.  Installez ce module (`sale_construction_billing`).

## Configuration

Aucune configuration complexe n'est requise par défaut. Les fonctionnalités s'intègrent directement dans le flux de vente standard.

## Utilisation

### 1. Création du Devis
Créez un devis client standard dans l'application Ventes. Ajoutez les produits et services (lignes de commande) correspondant au marché.

### 2. Gestion de l'Avancement
Sur le bon de commande validé, vous passez par l'assistant de création de facture pour définir une "Situation" (pourcentage d'avancement ou montant fixe pour la période).

### 3. Facturation (Situations)
Lors de la création de la facture (Situation n°X), le module calcule automatiquement :
*   Le montant des travaux réalisés à ce stade.
*   Déduit les éventuelles avances précédentes.
*   Applique la Retenue de Garantie si configurée.
*   Déduit le Compte Prorata si applicable.

## Structure Technique

*   **Modèles étendus** : `sale.order`, `account.move`
*   **Rapports** : Modèles de factures adaptés pour afficher les détails des situations et les retenues.

