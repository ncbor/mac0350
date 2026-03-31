from sqlmodel import Session
from database import engine, create_db_and_tables
from models import ExtensionGroup, Event

def seed_data():
    create_db_and_tables()
    with Session(engine) as session:
        # Check if already seeded
        existing = session.query(ExtensionGroup).first()
        if existing:
            print("Database already seeded.")
            return

        g1 = ExtensionGroup(
            name="CodeLab",
            description="Grupo de extensão focado em ensino de desenvolvimento de software e projetos na USP.",
            logo_url="https://codelab.ime.usp.br/images/logo_codelab.png"
        )
        g2 = ExtensionGroup(
            name="USPGameDev",
            description="Grupo focado no estudo e desenvolvimento de jogos eletrônicos e analógicos.",
            logo_url="https://uspgamedev.org/assets/images/ugd_logo_horizontal.png"
        )
        g3 = ExtensionGroup(
            name="Hardware Livre",
            description="Focado em desenvolvimento e pesquisa de software e hardware livre e de código aberto.",
            logo_url="https://hardwarelivreusp.org/images/logo_hl.png"
        )

        session.add(g1)
        session.add(g2)
        session.add(g3)
        session.commit()
        
        session.refresh(g1)
        session.refresh(g2)

        e1 = Event(
            title="Aula de WebMAC #10",
            date="2026-04-10T10:00:00",
            description="Aula sobre Docker.",
            group_id=g1.id
        )
        e2 = Event(
            title="Game Jam Semestral",
            date="2026-05-15T18:00:00",
            description="Maratona de desenvolvimento de jogos em 48h.",
            group_id=g2.id
        )

        session.add(e1)
        session.add(e2)
        session.commit()

        print("Database seeded successfully.")

if __name__ == "__main__":
    seed_data()
