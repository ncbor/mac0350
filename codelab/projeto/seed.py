from sqlmodel import Session
from database import engine, create_db_and_tables
from models import ExtensionGroup, Event

def seed_data():
    create_db_and_tables()
    with Session(engine) as session:
        # Purgue db to allow re-seeding
        for group in session.query(ExtensionGroup).all():
            session.delete(group)
        for event in session.query(Event).all():
            session.delete(event)
        session.commit()

        groups = [
            ExtensionGroup(name="IMEsec", description="Grupo de extensão focado em aprender, estudar e se divertir com a segurança da informação, aberto a qualquer aluno, bastando ter interesse. Encontros de hacking, criptografia, proteção de um servidor, desafios e competições, aulas e palestras.", logo_url="https://www.ime.usp.br/media/ccex/imesec.png", website="https://imesec.ime.usp.br/"),
            ExtensionGroup(name="CodeLab", description="Grupo de extensão universitária que tem como objetivo estimular a inovação tecnológica na USP com iniciativas para complementar a formação dos estudantes para se tornarem engenheiros de software capazes de desenvolverem sistemas reais, escolas de férias voltadas ao desenvolvimento de projetos em equipe e hackatons.", logo_url="https://www.ime.usp.br/media/ccex/uspcodelab.png", website="https://codelab.ime.usp.br/"),
            ExtensionGroup(name="USPGameDev", description="Grupo de pesquisa e desenvolvimento de jogos da USP, tem como meta criar um ambiente no qual membros da comunidade USP interessados na criação de jogos digitais e analógicos possam pôr em prática o que aprenderam em seus cursos e desenvolver suas próprias ideias.", logo_url="https://www.ime.usp.br/media/ccex/uspgamedev.png", website="https://uspgamedev.org/"),
            ExtensionGroup(name="FLUSP", description="O FLUSP é um grupo de alunos de graduação da USP que tem como objetivo contribuir com projetos de software livre (Free/Libre/Open Source Software – FLOSS). Todos estão convidados a saber mais sobre o grupo e descobrir as principais conquistas alcançadas até o momento.", logo_url="https://www.ime.usp.br/media/ccex/flusp.png", website="https://flusp.ime.usp.br/"),
            ExtensionGroup(name="MaratonUSP", description="Oferecimento de aulas, treinos e divulgação de materiais de apoio para a Maratona de Programação, Olimpíada Brasileira de Informática (OBI), e outras competições de programação.", logo_url="https://www.ime.usp.br/media/ccex/maratona.png", website="https://www.ime.usp.br/~maratona/"),
            ExtensionGroup(name="TECS", description="Focado no impacto social da computação e da tecnologia. Ele é parte do TechShift, uma aliança global de organizações estudantis com esse mesmo propósito.", logo_url="https://www.ime.usp.br/media/ccex/tecs.png", website="https://www.ime.usp.br/~tecs/"),
            ExtensionGroup(name="BeeData", description="Organização de estudantes, profissionais e entusiastas em ciência de dados interessados em desenvolver habilidades técnicas e participar de competições na área. Primeira liga competitiva de ciência de dados da USP.", logo_url="https://www.ime.usp.br/media/beedata-1024x1024.png", website="https://www.facebook.com/BeeDataUSP/"),
            ExtensionGroup(name="LEARN", description="O LEARN é um grupo de estudos com foco em Aprendizado de Máquina. Com encontros semanais, focamos em proatividade e desenvolvimento de projetos, levamos alunos do básico a projetos de alto impacto e participação em eventos renomados.", logo_url="https://www.ime.usp.br/media/learn.jpg", website="https://www.instagram.com/learnimeusp"),
            ExtensionGroup(name="USPAudioTech", description="O objetivo do grupo é desenvolver software e hardware para áudio e música digital, e empoderar pessoas interessadas nessa área de conhecimento, oferecendo recursos educacionais e suporte para criar ferramentas de qualidade, sempre com uma abordagem multidisciplinar e colaborativa. Simultaneamente, busca-se celebrar a música em sua diversidade e fortalecer a comunidade musical do IME.", logo_url="https://www.ime.usp.br/media/usp_audiotech.jpg", website="https://www.instagram.com/uspaudiotech"),
            ExtensionGroup(name="SymComp", description="Grupo que promove eventos e iniciativas relacionadas à área de computação para pessoas de dentro e fora da universidade. A SymComp organiza a Semana da Computação do IME-USP, o ByteCafé (visitas monitoradas de alunos do ensino médio) e a cerimônia do Prêmio PIPA. Seu objetivo é complementar a formação acadêmica com experiências reais e estimular conexões que promovam diferentes conteúdos da área de computação, conectando a universidade à sociedade.", logo_url="https://www.ime.usp.br/media/symcomp.jpg", website="https://symcomp.ime.usp.br/")
        ]

        for g in groups:
            session.add(g)
        session.commit()
        
        for g in groups:
            session.refresh(g)

        usp_codelab = next((g for g in groups if g.name == "CodeLab"), groups[0])
        usp_gamedev = next((g for g in groups if g.name == "USPGameDev"), groups[0])

        e1 = Event(
            title="Aula de WebMAC #10",
            date="2026-04-10T10:00:00",
            location="Sala 141, Bloco A",
            description="Aula sobre Docker.",
            group_id=usp_codelab.id
        )
        e2 = Event(
            title="Game Jam Semestral",
            date="2026-05-15T18:00:00",
            location="Auditório Jacy Monteiro",
            description="Maratona de desenvolvimento de jogos em 48h.",
            group_id=usp_gamedev.id
        )

        session.add(e1)
        session.add(e2)
        session.commit()

        print("Database seeded successfully.")

if __name__ == "__main__":
    seed_data()
